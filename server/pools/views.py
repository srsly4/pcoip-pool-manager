import json
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from .models import Pool

def login(request):
    """
    View responsible for logging user by the given credentials using Django session manager
    :param request: HTTPRequest, body made of JSON containing fields "username" and "password"
    :return: 200 if user exists
    :raise: 404 if login fails due to unrecognized username or password
    """
    if request.method == 'POST':
        try:
            json_body = json.loads(request.body)
            username, password = json_body['username'], json_body['password']
            assert username is not None and password is not None
        except (TypeError, AssertionError, KeyError):
            return HttpResponseBadRequest("Incorrect request body")
        user = authenticate(username=username, password=password)
        if user is not None:
            return HttpResponse(status=200)
        else:
            return HttpResponseNotFound("Login failed")


def reservation(request):
    pass


def pools_list(request):
    if request.method == 'GET':
        pools = list(Pool.objects.values())
        for p in pools:
            del p['id']
        json_pools = json.dumps({"pools": pools})
        return HttpResponse(json_pools, content_type="application/json")
    elif request.method == 'POST':
        pools = request.body.decode()
        pools_json = json.loads(pools)['pools']
        to_add = []
        try:
            for pool in pools_json:
                p = Pool(pool_id=pool['pool_id'], displayName=pool['displayName'], maximumCount=int(pool['maximumCount']),
                         enabled=bool(pool['enabled']), description=pool['description'])
                to_add.append(p)
        except Exception:
            return HttpResponseBadRequest("Incorrect pools description")
        Pool.objects.all().delete()
        for p in to_add:
            p.save()
        return HttpResponse("Pools added to database")
