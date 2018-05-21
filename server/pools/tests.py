import json
from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIRequestFactory
from .models import Pool, Reservation
from .views import Authentication


# Create your tests here.


class ModelTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=10)
        self.user = User.objects.create(username="test", password="test")
        Reservation.objects.create(pool_id=self.pool.id, user_id=self.user.id, slot_count=5,
                                   start_datetime=datetime(2018, 4, 1, 11, 15),
                                   end_datetime=datetime(2018, 4, 1, 12, 45))

    # def test_can_place_reservation(self):
    #     self.assertTrue(self.pool.can_place_reservation(3, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))
    #
    # def test_cannot_place_reservation(self):
    #     self.assertFalse(self.pool.can_place_reservation(7, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))


class TestSimpleReservedSlots(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=10)
        self.user = User.objects.create(username="test", password="test")

    def test_no_reservation(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 15), datetime(2018, 4, 1, 12, 15)),
            0)


class TestSingleReservedSlots(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=10)
        self.pool.save()
        self.user = User.objects.create_user(username="test", password="test", is_active=True)
        self.user.save()
        self.res = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user.id, slot_count=5,
                                              start_datetime=datetime(2018, 4, 1, 11, 15),
                                              end_datetime=datetime(2018, 4, 1, 12, 45))
        self.res.save()

    def test_reservation_before(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 10, 00), datetime(2018, 4, 1, 11, 10)),
            0)
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 10, 15), datetime(2018, 4, 1, 11, 15)),
            0)

    def test_reservation_after(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 12, 50), datetime(2018, 4, 1, 12, 55)),
            0)
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 12, 45), datetime(2018, 4, 1, 12, 55)),
            0)

    def test_reservation_inside(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 20), datetime(2018, 4, 1, 12, 40)),
            5)
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 15), datetime(2018, 4, 1, 12, 45)),
            5)

    def test_reservation_right_overlap(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 12, 00)),
            5)

    def test_reservation_left_overlap(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 12, 00), datetime(2018, 4, 1, 13, 00)),
            5)

    def test_reservation_overlap(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)),
            5)


class TestMultipleReservedSlot(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=100)
        self.pool.save()
        self.user1 = User.objects.create_user(username="test1", password="test1", is_active=True)
        self.user1.save()
        self.user2 = User.objects.create_user(username="test2", password="test2", is_active=True)
        self.user2.save()
        self.user3 = User.objects.create_user(username="test3", password="test3", is_active=True)
        self.user3.save()
        self.user4 = User.objects.create_user(username="test4", password="test4", is_active=True)
        self.user4.save()
        self.res1 = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user1.id, slot_count=5,
                                               start_datetime=datetime(2018, 4, 1, 11, 15),
                                               end_datetime=datetime(2018, 4, 1, 12, 45))
        self.res1.save()
        self.res2 = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user1.id, slot_count=10,
                                               start_datetime=datetime(2018, 4, 1, 13, 00),
                                               end_datetime=datetime(2018, 4, 1, 15, 00))
        self.res2.save()
        self.res3 = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user2.id, slot_count=15,
                                               start_datetime=datetime(2018, 4, 1, 12, 00),
                                               end_datetime=datetime(2018, 4, 1, 14, 00))
        self.res3.save()
        self.res4 = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user3.id, slot_count=20,
                                               start_datetime=datetime(2018, 4, 1, 12, 50),
                                               end_datetime=datetime(2018, 4, 1, 16, 00))
        self.res4.save()
        self.res5 = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user1.id, slot_count=20,
                                               start_datetime=datetime(2018, 4, 1, 17, 00),
                                               end_datetime=datetime(2018, 4, 1, 18, 00))
        self.res5.save()

    def test_overlapping_reservations(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 30), datetime(2018, 4, 1, 13, 00)),
            40)
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 12, 50)),
            20)
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 18, 00)),
            45)

    def test_non_overlapping_reservations(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 30), datetime(2018, 4, 1, 13, 00)),
            40)



class LoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="testpassword", is_active=True)
        self.user.save()

    def test_login_correct(self):
        correct_request = self.client.post("/auth/", json.dumps({"username": "test", "password": "testpassword"}),
                                           content_type="application/json")
        self.assertEqual(correct_request.status_code, status.HTTP_200_OK)

    def test_login_incorrect(self):
        incorrect_request = self.client.post("/auth/", json.dumps({"field": "test"}),
                                             content_type="application/json")
        self.assertEqual(incorrect_request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_no_such_user(self):
        no_such_user_request = self.client.post("/auth/", json.dumps({"username": "tset", "password": "tset"}),
                                                content_type="application/json")
        self.assertEqual(no_such_user_request.status_code, status.HTTP_404_NOT_FOUND)


class PoolsTest(TestCase):
    def setUp(self):
        self.pool1 = Pool.objects.create(pool_id="id1", displayName="name1", maximumCount=10,
                                         enabled=True, description="desc1")
        self.pool2 = Pool.objects.create(pool_id="id2", displayName="name2", maximumCount=20,
                                         enabled=False, description="desc2")
        self.pool1.save()
        self.pool2.save()

    def test_get(self):
        data = self.client.get("/pools/")
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        j = json.loads(data.content.decode())["pools"]
        p1 = {"pool_id": self.pool1.pool_id, "displayName": self.pool1.displayName,
              "maximumCount": self.pool1.maximumCount,
              "enabled": self.pool1.enabled, "description": self.pool1.description}
        p2 = {"pool_id": self.pool2.pool_id, "displayName": self.pool2.displayName,
              "maximumCount": self.pool2.maximumCount,
              "enabled": self.pool2.enabled, "description": self.pool2.description}
        self.assertTrue(p1 in j)
        self.assertTrue(p2 in j)

    def test_post(self):
        p1 = {"pool_id": self.pool1.pool_id, "displayName": self.pool1.displayName,
              "maximumCount": self.pool1.maximumCount,
              "enabled": self.pool1.enabled, "description": self.pool1.description}
        p2 = {"pool_id": self.pool2.pool_id, "displayName": self.pool2.displayName,
              "maximumCount": self.pool2.maximumCount,
              "enabled": self.pool2.enabled, "description": self.pool2.description}
        p3 = {"pool_id": "id3", "displayName": "disp3name", "maximumCount": 50,
              "enabled": False, "description": "description3"}
        p4 = {"pool_id": "id4", "displayName": "disp4name", "maximumCount": 8,
              "enabled": True, "description": "description4"}
        js = json.dumps({"pools": [p3, p4]})
        data = self.client.post("/pools/", js, content_type="application/json")
        self.assertEquals(status.HTTP_201_CREATED, data.status_code)
        data = self.client.get("/pools/")
        j = json.loads(data.content.decode())["pools"]
        self.assertFalse(p1 in j)
        self.assertFalse(p2 in j)
        self.assertTrue(p3 in j)
        self.assertTrue(p4 in j)
