import json

from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound


# Create your views here.


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
