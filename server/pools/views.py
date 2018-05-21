import json
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
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


# class Reservation(APIView):
#     pass


class PoolsList(APIView):
    parser_classes = (JSONParser,)

    def get(self, request):
        pools = list(Pool.objects.values())
        for p in pools:
            del p['id']
        json_pools = {"pools": pools}
        return Response(data=json_pools, content_type="application/json")

    def post(self, request):
        pools_json = request.data['pools']
        to_add = []
        try:
            for pool in pools_json:
                p = Pool(pool_id=pool['pool_id'], displayName=pool['displayName'],
                         maximumCount=int(pool['maximumCount']),
                         enabled=bool(pool['enabled']), description=pool['description'])
                to_add.append(p)
        except Exception:
            return Response("Incorrect pools description", status=HTTP_400_BAD_REQUEST)
        Pool.objects.all().delete()
        for p in to_add:
            p.save()
        return Response("Pools added to database", status=HTTP_201_CREATED)
