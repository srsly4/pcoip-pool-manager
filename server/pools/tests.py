from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIRequestFactory
from server.pools.models import Pool, Reservation
from server.pools.views import login


class ModelTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=10)
        self.user = User.objects.create(username="test", password="test")
        Reservation.objects.create(pool_id=self.pool.id, user_id=self.user.id, count=5,
                                   start_datetime=datetime(2018, 4, 1, 11, 15),
                                   end_datetime=datetime(2018, 4, 1, 12, 45))

    def test_already_reserved_slots(self):
        self.assertEqual(self.pool.already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 12, 30)),
                         5)

    def test_can_place_reservation(self):
        self.assertTrue(self.pool.can_place_reservation(3, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))
        self.assertFalse(self.pool.can_place_reservation(7, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))


class LoginTest(TestCase):
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


class PoolsTest(TestCase):
    def setUp(self):
        Pool.objects.create(pool_id='id1', displayName='name1', maximumCount=10,
                         enabled=True, description='desc1')
        Pool.objects.create(pool_id='id2', displayName='name2', maximumCount=20,
                            enabled=False, description='desc2')

    def test_get(self):
        data = Pool.objects.all()
        self.assertEquals(len(data), 2)
        self.assertTrue(Pool.objects.all().contains(Pool(pool_id='id1', displayName='name1', maximumCount=10,
                            enabled=False, description='desc1')))
        self.assertTrue(Pool.objects.all().contains(Pool(pool_id='id2', displayName='name2', maximumCount=20,
                                                         enabled=False, description='desc2')))