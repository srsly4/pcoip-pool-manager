import csv
import io
import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Pool, Reservation
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from .models import Pool


class Authentication(APIView):
    """
    View responsible for logging user by the given credentials using Django session manager
    """
    parser_classes = (JSONParser,)

    def post(self, request):
        """
        :param request: HTTPRequest, body made of JSON containing fields "username" and "password"
        :return: 200 if user exists
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
            return Response()
        else:
            return Response(data="Login failed", status=HTTP_404_NOT_FOUND)


# TODO: move to different location
def process_row(row):
    for i in range(len(row)):
        row[i] = row[i].replace('\n', ' ')
    row[2] = int(row[2])
    row[3] = True if row[3] == "true" else False
    return tuple(row)


class Reservations(APIView):
    """
    View responsible for adding new reservations and getting list of all reservations
    """
    parser_classes = (JSONParser,)

    def get(self, request):
        filters = {}
        start_datetime = request.GET.get('sd')
        if start_datetime is not None:
            filters["start_datetime__gte"] = start_datetime
        end_datetime = request.GET.get('ed')
        if end_datetime is not None:
            filters["end_datetime__lte"] = end_datetime
        pid = request.GET.get('pid')
        if pid is not None:
            pool_id = Pool.objects.get(pool_id=pid).id
            filters["pool_id"] = pool_id
        uid = request.GET.get('uid')
        if uid is not None:
            user_id = User.objects.get(username=uid).id
            filters["user_id"] = user_id
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
        # TODO: doscuss file format
        pass


class PoolsList(APIView):
    """
    View responsible for updating pools list and getting list of pools
    """
    parser_classes = (MultiPartParser,)

    def get(self, request):
        pools = list(Pool.objects.values())
        for p in pools:
            del p['id']
        json_pools = json.dumps({"pools": pools})
        return Response(json_pools, content_type="application/json")

    def post(self, request):
        file = request.data['pools']
        print("file: " + str(file))
        content = io.StringIO(file.file.read().decode('utf-8'))
        reader = csv.reader(content, delimiter=',')
        next(reader)
        pools = [process_row(row) for row in reader]
        to_add = []
        try:
            for pool in pools:
                p = Pool(pool_id=pool[0], displayName=pool[1], maximumCount=pool[2], enabled=pool[3], description=pool[4])
                to_add.append(p)
        except Exception:
            return Response("Incorrect pools description", status=HTTP_400_BAD_REQUEST)
        Pool.objects.all().delete()
        for p in to_add:
            p.save()
        return Response("Pools added to database", status=HTTP_201_CREATED)
