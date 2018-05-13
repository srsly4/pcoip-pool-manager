import json
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from .models import Pool, Reservation
from .views import login

# Create your tests here.


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
        self.pool1 = Pool.objects.create(pool_id='id1', displayName='name1', maximumCount=10,
                                         enabled=True, description='desc1')
        self.pool2 = Pool.objects.create(pool_id='id2', displayName='name2', maximumCount=20,
                                         enabled=False, description='desc2')
        self.pool1.save()
        self.pool2.save()

    def test_get(self):
        data = self.client.get("/pools/")
        self.assertEquals(200, data.status_code)
        j = json.loads(data.content.decode())['pools']
        p1 = {"pool_id": self.pool1.pool_id, "displayName": self.pool1.displayName, "maximumCount": self.pool1.maximumCount,
              "enabled": self.pool1.enabled, "description": self.pool1.description}
        p2 = {"pool_id": self.pool2.pool_id, "displayName": self.pool2.displayName, "maximumCount": self.pool2.maximumCount,
              "enabled": self.pool2.enabled, "description": self.pool2.description}
        self.assertTrue(p1 in j)
        self.assertTrue(p2 in j)

    def test_post(self):
        p1 = {"pool_id": self.pool1.pool_id, "displayName": self.pool1.displayName, "maximumCount": self.pool1.maximumCount,
              "enabled": self.pool1.enabled, "description": self.pool1.description}
        p2 = {"pool_id": self.pool2.pool_id, "displayName": self.pool2.displayName, "maximumCount": self.pool2.maximumCount,
              "enabled": self.pool2.enabled, "description": self.pool2.description}
        p3 = {"pool_id": "id3", "displayName": "disp3name", "maximumCount": 50,
              "enabled": False, "description": "description3"}
        p4 = {"pool_id": "id4", "displayName": "disp4name", "maximumCount": 8,
              "enabled": True, "description": "description4"}
        js = json.dumps({"pools": [p3, p4]})
        file = SimpleUploadedFile("pools", b'''
        "pool_id","displayName","maximumCount","enabled","description"
        "s7n-girls","Green Lights 4 Girls (Win7)",2,"false","View Agent (6.2.2) Firefox (55.0.3), Chrome (61.0), Flash (27.0.0), Libre Office (5.4.1.2), Adobe Reader DC (17.012), JRE (8u144)"
        "s7n-gram","Gramatyki grafowe(Win7)",2,"false","View Agent (6.0.1) oraz Firefox (44.0.2), Chrome (49.0), IE (10), Flash (20.0.0), Adobe Reader DC (15.010), Libre Office (5.1.0), JRE 8u73 Dograne, a nie instalowane: GraphTool i LineTree 3D"'))
        ''', content_type='file')
        file.name = 'pools'
        self.client.post("/pools/", {'pools' : file}, content_type="file")
        # data = self.client.post("/pools/", js, content_type="application/json")
        # self.assertEquals(200, data.status_code)
        # data = self.client.get("/pools/")
        # j = json.loads(data.content.decode())['pools']
        # self.assertFalse(p1 in j)
        # self.assertFalse(p2 in j)
        # self.assertTrue(p3 in j)
        # self.assertTrue(p4 in j)

