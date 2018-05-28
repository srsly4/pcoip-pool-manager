import csv
import io
from datetime import timedelta, datetime

from django.contrib.auth import authenticate
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

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
        canceled = Reservation.objects.filter(id=body['id']).delete()
        status = HTTP_204_NO_CONTENT if canceled[0] else HTTP_404_NOT_FOUND
        return Response(status=status)


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
        filters = {}
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
        json_reservations = {"reservations": [parse_utils.make_JSON(r) for r in reservations]}
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
        print("!!!!!!!")
        print(request.data.keys())
        file = request.data['reservations']

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

                    if res['peroid'] <= 0:
                        break
                    start += timedelta(days=res['peroid'])
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
