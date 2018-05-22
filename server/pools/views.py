import csv
import io
import json
from datetime import timedelta, datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from .models import Pool, Reservation, ExpirableToken
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from .models import Pool
from pools.utils import parse_utils


class Authentication(APIView):
    """
    View responsible for logging user by the given credentials using Django session manager
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: HTTPRequest, body made of JSON containing fields "username" and "password"
        :return: 200 if user exists, message body contains string token needed for further operations
        :raise: 404 if login fails due to unrecognized username or password
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
    parser_classes = (JSONParser, )

    def post(self, request):
        """
        :param request: HTTPRequest, body made of JSON containing pool_id, slot_count, start_datetime and end_datetime
        :return: 201 if reservation is added to database
        :raise: 409 if reservation can't be added to database
        """
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

    def delete(self, request):
        """
        :param request: HTTPRequest, JSON body with 'id' of reservation to delete
        :return: 204 if reservation is deleted
        :raise: 404 if reservation doesn't exist
        """
        body = request.data
        canceled = Reservation.objects.filter(id=body['id']).delete()
        status = HTTP_204_NO_CONTENT if canceled[0] else HTTP_404_NOT_FOUND
        return Response(status=status)

class Reservations(APIView):
    """
    View responsible for adding new reservations and getting list of all reservations
    """
    parser_classes = (JSONParser,)

    def get(self, request):
        """
        :param request: HTTPRequest used only to authenticate user
        :parameter start: start of time interval in which reservations are searched, not required
        :parameter end: end of time interval in which reservations are searched, not required
        :parameter pid: id of pool to search, not required
        :return: 200, contains json with all reservations
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
        json_reservations = [r.__dict__ for r in reservations]
        for r in json_reservations:
            del r['id']
            del r['_state']
            r['start_datetime'] = str(r['start_datetime'])
            r['end_datetime'] = str(r['end_datetime'])
        json_reservations = json.dumps({"reservations": json_reservations})
        return Response(json_reservations, content_type="application/json")

    def post(self, request):
        """
        :param request: HTTPRequest containing file(named 'reservations') with reservations list
        :return: 201 if reservations has been added to database
        :raise: 409 if there is a conflict with different reservations,
                response text contains list of impossible reservations
        :raise: 400 if file format isn't correct
        """
        file = request.data['reservations']
        content = io.StringIO(file.file.read().decode('utf-8'))
        reader = csv.reader(content, delimiter=',')
        next(reader)
        reservations = [parse_utils.process_reservation_row(row) for row in reader]
        to_add = []
        not_possible = []
        try:
            for res in reservations:
                start = res['start_date']
                end = res['end_date']
                while start <= end:
                    start_time = datetime.datetime.combine(start, res['start_time'])
                    end_time = datetime.datetime.combine(start, res['end_time'])
                    user = request.user
                    r = Reservation(pool=res['pool_id'], user=user, slot_count=res['slot_count'],
                                    start_datetime= start_time,
                                    end_datetime=end_time)
                    if Pool.object.get(pool_id=res['pool_id']).can_place_reservation(res['slot_count'],
                                                                                     start_time, end_time):
                        to_add.append(r)
                    else:
                        not_possible.append('pool_id')
                    start += timedelta(days=res['peroid'])
        except Exception:
            return Response("Incorrect reservation description", status=HTTP_400_BAD_REQUEST)
        if len(not_possible) > 0:
            text = "Cannot make reservation on slots:\n"
            for np in not_possible:
                text += "\t" + np + "\n"
            return Response(text, status=HTTP_409_CONFLICT)
        for r in to_add:
            r.save()
        return Response("Reservations added to database", status=HTTP_201_CREATED)


class PoolsList(APIView):
    """
    View responsible for updating pools list and getting list of pools
    """
    parser_classes = (MultiPartParser,)
    renderer_classes = (JSONRenderer, )

    def get(self, request):
        """
        :param request: used only for authentication
        :return: 200 with a JSON containing all pools
        """
        pools = list(Pool.objects.values())
        for p in pools:
            del p['id']
        return Response(pools, content_type="application/json")

    def post(self, request):
        """
        :param request: HTTPRequest containing file(named 'pools') with pools description
        :return: 201 if pools has been added to database
        :raise: 400 if file format isn't correct
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
