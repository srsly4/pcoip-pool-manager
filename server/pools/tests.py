from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIRequestFactory

from .models import Pool, Reservation


# Create your tests here.
from .views import login


class ModelTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=10)
        self.user = User.objects.create(username="test", password="test")
        Reservation.objects.create(pool_id=self.pool.id, user_id=self.user.id, slot_count=5,
                                   start_datetime=datetime(2018, 4, 1, 11, 15),
                                   end_datetime=datetime(2018, 4, 1, 12, 45))

    def test_already_reserved_slots(self):
        self.assertEqual(self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 12, 30)),
                         5)

    def test_can_place_reservation(self):
        self.assertTrue(self.pool.can_place_reservation(3, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))
        self.assertFalse(self.pool.can_place_reservation(7, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))


class ApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test", password="testpassword", is_active=True)
        self.user.set_password("testpassword")
        self.user.save()
        self.client = Client()
        self.factory = APIRequestFactory()

    def test_login_post(self):
        correct_request = self.factory.post(path="/login/", data={"username": "test", "password": "testpassword"},
                                            format="json")
        incorrect_request = self.factory.post(path="/login/", data={"field": "test"}, format="json")
        no_such_user_request = self.factory.post(path="/login/", data={"username": "tset", "password": "tset"},
                                                 format="json")
        self.assertEqual(login(correct_request).status_code, status.HTTP_200_OK)
        self.assertEqual(login(incorrect_request).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(login(no_such_user_request).status_code, status.HTTP_404_NOT_FOUND)
