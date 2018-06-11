import csv
import io
import time
from datetime import timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.db.models import Q
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from pcoippoolmanager import settings
from .models import Pool
from .models import Reservation, ExpirableToken
from .utils import parse_utils


class Authentication(APIView):
    """
    View responsible for logging user by the given credentials using Django session manager
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param: JSON body containing fields "username" and "password" \n
        :return: 200 if user exists, message body contains string token needed for further operations \n
        :raise: 404 if login fails due to unrecognized username or password \n
        :raise: 400 if login fails due to incorrect request body \n
        Important! No 'Authorization' header here, otherwise errors will be thrown!
        """
        try:
            json_body = request.data
            username, password = json_body['username'], json_body['password']
            assert username is not None and password is not None
        except (TypeError, AssertionError, KeyError):
            return Response("Incorrect request body", status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is not None:
            token = ExpirableToken.objects.get_or_create(user=user)[0].replace()
            return Response(data=token.key)
        else:
            return Response(data="Login failed", status=HTTP_404_NOT_FOUND)


class SingleReservation(APIView):
    """
    View responsible for adding a single reservation to database
    """
    parser_classes = (JSONParser,)

    def post(self, request):
        """
        :param: JSON body containing pool_id, slot_count, start_datetime and end_datetime \n
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :return: 201 if reservation is added to database \n
        :raise: 409 if reservation can't be added to database \n
        :raise: 401 if token authentication fails \n
        """
        try:
            body = request.data
            pool = Pool.objects.get(pool_id=body['pool_id'])
            if pool.can_place_reservation(body['slot_count'], body['start_datetime'], body['end_datetime']):
                reservation = Reservation(pool=pool, user=request.user, slot_count=body['slot_count'],
                                          start_datetime=body['start_datetime'],
                                          end_datetime=body['end_datetime'])
                reservation.save()
                return Response("Reservation added to database", HTTP_201_CREATED)
            else:
                return Response("Can't add reservation", HTTP_409_CONFLICT)
        except KeyError:
            return Response("Incorrect JSON format", HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        :param: JSON body with 'id' of reservation to delete \n
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :return: 204 if reservation is deleted \n
        :raise: 404 if reservation doesn't exist \n
        :raise: 401 if token authentication fails \n
        """
        body = request.data
        description = ""
        try:
            to_cancel = Reservation.objects.get(id=body['id'])
            to_cancel.is_canceled = True
            to_cancel.save()
            status = HTTP_204_NO_CONTENT
        except ObjectDoesNotExist:
            status = HTTP_404_NOT_FOUND
            description = "No such reservation exists"
        except KeyError:
            status = HTTP_400_BAD_REQUEST
            description = "No id field in body"
        except ValueError:
            status = HTTP_400_BAD_REQUEST
            description = "id is not an integer"
        return Response(description, status=status)


class Reservations(APIView):
    """
    View responsible for adding new reservations and getting list of all reservations
    """
    parser_classes = (JSONParser, FormParser, MultiPartParser,)

    def get(self, request):
        """
        :parameter start: start of time interval in which reservations are searched, not required \n
        :parameter end: end of time interval in which reservations are searched, not required \n
        :parameter pid: id of pool to search, not required \n
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :return: 200, contains json with all reservations \n
        :raise: 401 if token authentication fails \n
        """
        filters = {'is_canceled': False}
        start_datetime = request.GET.get('start')
        if start_datetime is not None:
            filters["start_datetime__gte"] = start_datetime
        end_datetime = request.GET.get('end')
        if end_datetime is not None:
            filters["end_datetime__lte"] = end_datetime
        pid = request.GET.get('pid')
        if pid is not None:
            pool = Pool.objects.get(pool_id=pid)
            filters["pool"] = pool
        user = request.user
        filters["user"] = user
        reservations = list(Reservation.objects.filter(**filters))
        json_reservations = {"reservations": [parse_utils.reservation_to_json(r) for r in reservations]}
        return Response(json_reservations, content_type="application/json")

    def post(self, request):
        """
        :param: File(named 'reservations') with reservations list \n
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :return: 201 if reservations has been added to database \n
        :raise: 409 if there is a conflict with different reservations,
                response text contains list of impossible reservations \n
        :raise: 400 if data provided isn't correct \n
        :raise: 401 if token authentication fails \n
        """
        try:
            file = request.data['reservations']
        except KeyError:
            return Response("No file included", status=HTTP_400_BAD_REQUEST)
        content = io.StringIO(file.file.read().decode('utf-8'))
        reader = csv.reader(content, delimiter=',')
        next(reader)
        try:
            reservations = [parse_utils.process_reservation_row(row) for row in reader]
        except (KeyError, ValueError):
            return Response("Wrong file format", status=HTTP_400_BAD_REQUEST)
        to_add = []
        not_possible = []
        user = request.user
        try:
            for res in reservations:
                start = res['start_date']
                end = res['end_date']
                while start <= end:
                    start_time = datetime.combine(start, res['start_time'])
                    end_time = datetime.combine(start, res['end_time'])
                    pool = Pool.objects.get(pool_id=res['pool_id'])
                    if pool.can_place_reservation(res['slot_count'], start_time, end_time):
                        r = Reservation(pool=pool, user=user, slot_count=res['slot_count'],
                                        start_datetime=start_time,
                                        end_datetime=end_time)
                        to_add.append(r)
                    else:
                        not_possible.append(('pool_id', start_time, end_time))

                    if res['period'] <= 0:
                        break
                    start += timedelta(days=res['period'])
        except Exception:
            return Response("Incorrect reservation description", status=HTTP_400_BAD_REQUEST)
        if len(not_possible) > 0:
            text = "Cannot make reservation on slots:\n"
            for np in not_possible:
                text += "\t" + np[0] + "from " + str(np[1]) + " to " + str(np[2]) + "\n"
            return Response(text, status=HTTP_409_CONFLICT)
        for r in to_add:
            r.save()
        return Response("Reservations added to database", status=HTTP_201_CREATED)


class PoolsList(APIView):
    """
    View responsible for updating pools list and getting list of pools
    """
    parser_classes = (MultiPartParser,)
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        """
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :return: 200 with a JSON containing all pools \n
        :raise: 401 if token authentication fails \n
        """
        pools = list(Pool.objects.values())
        for p in pools:
            del p['id']
        return Response(pools, content_type="application/json")

    def post(self, request):
        """
        :param: File(named 'pools') with pools description \n
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :return: 201 if pools has been added to database \n
        :raise: 400 if file format isn't correct \n
        :raise: 401 if token authentication fails \n
        """
        file = request.data['pools']
        content = io.StringIO(file.file.read().decode('utf-8'))
        reader = csv.reader(content, delimiter=',')
        next(reader)
        pools = [parse_utils.process_pool_description_row(row) for row in reader]
        to_add = []
        try:
            for pool in pools:
                p = Pool(pool_id=pool[0], displayName=pool[1], maximumCount=pool[2],
                         enabled=pool[3], description=pool[4])
                to_add.append(p)
        except Exception:
            return Response("Incorrect pools description", status=HTTP_400_BAD_REQUEST)
        Pool.objects.all().delete()
        for p in to_add:
            p.save()
        return Response("Pools added to database", status=HTTP_201_CREATED)


class MailView(APIView):
    """
    View responsible for sending emails
    """
    parser_classes = (JSONParser,)

    def post(self, request):
        """
        :param: JSON containing field 'content', and optional field 'reply_email'\n
        :return: 200 if message has been sent\n
        :raise: 401 if token authentication fails \n
        :raise: 400 if no content has been specified\n
        :raise: 500 if message could not be sent
        """
        try:
            content = request.data['content']
        except KeyError:
            return Response('No message content has been specified', status=HTTP_400_BAD_REQUEST)
        try:
            reply_address = request.data['reply_address']
        except KeyError:
            reply_address = request.user.email
        admins = list(User.objects.filter(is_superuser=True))
        recipients = [user.email for user in admins]
        mail = EmailMessage('PCOIPPM message',
                            content,
                            settings.DEFAULT_FROM_EMAIL,
                            recipients,
                            headers={'Reply-To': reply_address})
        try:
            mail.send()
        except Exception as e:
            return Response('Sending message failed\n' + str(e), status=HTTP_500_INTERNAL_SERVER_ERROR)
        return Response('Email sent', status=HTTP_200_OK)


class Statistics(APIView):
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get(self, request):
        """
        :param: 'Authorization' header containing valid token, prepended with :keyword 'Token', for example 'Token 123'
        \n
        :param: start - datetime in format %Y-%m-%d-%H-%M, if not given will be set to 01.01.1970 00:01 \n
        :param: end - datetime in format %Y-%m-%d-%H-%M, if not given will be set to current datetime \n
        :return: 200, json with fields start, end (datetimes in format %Y-%m-%d-%H-%M),
        most_used and least_used (lists of pairs (pool_id, count of reservations in given timeslot)) \n
        :raise: 401 if authentication fails \n
        :raise: 400 if start datetime is later than end or arguments contain either incorrect data format
        or something else entirely
        """
        try:
            if request.GET.get('start') is not None:
                _start_datetime = datetime.strptime(request.GET.get('start'), "%Y-%m-%d-%H-%M")
            else:
                _start_datetime = datetime(1970, 1, 1, 0, 1, 0, 0)
            if request.GET.get('end') is not None:
                _end_datetime = datetime.strptime(request.GET.get('end'), "%Y-%m-%d-%H-%M")
            else:
                _end_datetime = datetime.now()
        except (TypeError, ValueError):
            return Response(status=HTTP_400_BAD_REQUEST, data="Incorrect date format")
        if _start_datetime > _end_datetime:
            return Response(status=HTTP_400_BAD_REQUEST, data="Start date after end")
        reservations_in_timeslot = Reservation.objects.filter(Q(pool__enabled=True),
                                                              Q(start_datetime__gt=_start_datetime,
                                                                start_datetime__lt=_end_datetime) |
                                                              Q(end_datetime__lt=_end_datetime,
                                                                end_datetime__gt=_start_datetime)).distinct()
        pairs = []
        for pool in Pool.objects.all():
            pairs.append((pool.pool_id, reservations_in_timeslot.filter(pool=pool).count()))
        pairs.sort(key=lambda element: element[1])
        least_used = pairs[:10]
        most_used = pairs[:]
        most_used.reverse()
        most_used = most_used[:10]
        json_map = {'start': _start_datetime.strftime("%Y-%m-%d-%H-%M"),
                    'end': _end_datetime.strftime("%Y-%m-%d-%H-%M"), 'most_used': most_used,
                    'least_used': least_used}
        return Response(data=json_map, status=HTTP_200_OK)
