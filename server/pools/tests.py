import json
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Pool, Reservation, ExpirableToken
from .views import Authentication, PoolsList, SingleReservation, Reservations


# Create your tests here.


class ModelTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="1", displayName="1", maximumCount=10)
        self.user = User.objects.create(username="test", password="test")
        Reservation.objects.create(pool_id=self.pool.id, user_id=self.user.id, slot_count=5,
                                   start_datetime=datetime(2018, 4, 1, 11, 15),
                                   end_datetime=datetime(2018, 4, 1, 12, 45))

    def test_already_reserved_slots(self):
        self.assertEqual(
            self.pool.calculate_already_reserved_slots(datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 12, 30)),
            5)

    def test_can_place_reservation(self):
        self.assertTrue(self.pool.can_place_reservation(3, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))

    def test_cannot_place_reservation(self):
        self.assertFalse(self.pool.can_place_reservation(7, datetime(2018, 4, 1, 11, 00), datetime(2018, 4, 1, 13, 00)))


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
        self.user = User.objects.create_user(username="user", password="testtesttest", email="testmail@mail.mail")
        self.user.save()
        token = ExpirableToken.objects.create(user=self.user, key=123123123123)
        token.save()
        self.key = token.key
        self.factory = APIRequestFactory()
        self.view = PoolsList.as_view()

    def test_get(self):
        request = self.factory.get("/pools/")
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        j = json.loads(data.content.decode())
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

        file_text = '''"pool_id","displayName","maximumCount","enabled","description"
"id3","disp3name",50,"false","description3"
"id4","disp4name",8,"true","description4"
'''
        file = SimpleUploadedFile('pools.csv', file_text.encode())
        request = self.factory.post("/pools/", data={'pools': file}, format='multipart')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_201_CREATED, data.status_code)
        request = self.factory.get("/pools/")
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        j = json.loads(data.content.decode())
        self.assertFalse(p1 in j)
        self.assertFalse(p2 in j)
        self.assertTrue(p3 in j)
        self.assertTrue(p4 in j)

class SingleReservationTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="id1", displayName="name1", maximumCount=10,
                                         enabled=True, description="desc1")
        self.pool.save()

        self.user = User.objects.create_user(username="user", password="testtesttest", email="testmail@mail.mail")
        self.user.save()
        token = ExpirableToken.objects.create(user=self.user, key=123123123123)
        token.save()
        self.key = token.key
        self.factory = APIRequestFactory()
        self.view = SingleReservation.as_view()

    def test_success_post(self):
        data = {"pool_id": "id1", "slot_count": 2, "start_datetime": "2018-05-20 12:00",
                "end_datetime": "2018-05-20 14:00"}
        request = self.factory.post("/pools/", data=data, format='json')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_201_CREATED, data.status_code)
        res = Reservation.objects.filter(pool=self.pool)
        self.assertEqual(len(res), 1)

    def test_fail_post(self):
        data = {"pool_id": "id1", "slot_count": 50, "start_datetime": "2018-05-20 12:00",
                "end_datetime": "2018-05-20 14:00"}
        request = self.factory.post("/pools/", data=data, format='json')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_409_CONFLICT, data.status_code)
        res = Reservation.objects.filter(pool=self.pool)
        self.assertEqual(len(res), 0)

    def create_reservation(self):
        res = Reservation.objects.create(
            pool=self.pool, user=self.user, slot_count=1,
            start_datetime=datetime(2018, 4, 1, 11, 15),
            end_datetime=datetime(2018, 4, 1, 12, 15)
        )
        res.save()
        return res.id

    def get_response(self, res_id):
        request = self.factory.delete(
            "/reservation/",
            data={"id": res_id},
            format='json'
        )
        force_authenticate(request, self.user, self.key)
        response = self.view(request).render()
        return response

    def check_if_is_deleted(self, res_id):
        reservation_num = len(Reservation.objects.filter(id=res_id))
        self.assertEqual(reservation_num, 0)

    def test_delete(self):
        total_res = 5
        reservation_id = [self.create_reservation() for _ in range(total_res)]

        response = self.get_response(reservation_id[0])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.check_if_is_deleted(reservation_id[0])

        for i in range(1, total_res):
            reservation_num = len(Reservation.objects.filter(id=reservation_id[i]))
            self.assertEqual(reservation_num, 1)

    def test_double_delete(self):
        res_id = self.create_reservation()
        response = self.get_response(res_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.check_if_is_deleted(res_id)
        response = self.get_response(res_id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_never_existed(self):
        res_id = self.create_reservation()
        self.check_if_is_deleted(res_id + 1)
        response = self.get_response(res_id + 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




class ReservationsTestGet(TestCase):
    def setUp(self):
        self.pool1 = Pool.objects.create(pool_id="id1", displayName="name1", maximumCount=10,
                                        enabled=True, description="desc1")
        self.pool1.save()
        self.pool2 = Pool.objects.create(pool_id="id2", displayName="name2", maximumCount=20,
                                        enabled=True, description="desc2")
        self.pool2.save()
        self.user1 = User.objects.create_user(username="user1", password="testtesttest1", email="testmail1@mail.mail")
        self.user1.save()
        self.user2 = User.objects.create_user(username="user2", password="testtesttest2", email="testmail2@mail.mail")
        self.user2.save()
        token1 = ExpirableToken.objects.create(user=self.user1, key=123123123123)
        token1.save()
        self.key1 = token1.key
        token2 = ExpirableToken.objects.create(user=self.user2, key=321321321321)
        token2.save()
        self.key2 = token2.key
        self.res1 = Reservation.objects.create(pool=self.pool1, user=self.user1, slot_count=5,
                                               start_datetime=datetime(2018, 4, 1, 11, 15),
                                               end_datetime=datetime(2018, 4, 1, 12, 45))
        self.res1.save()
        self.res2 = Reservation.objects.create(pool=self.pool1, user=self.user1, slot_count=5,
                                               start_datetime=datetime(2018, 4, 1, 13, 15),
                                               end_datetime=datetime(2018, 4, 1, 15, 45))
        self.res2.save()
        self.res3 = Reservation.objects.create(pool=self.pool2, user=self.user2, slot_count=4,
                                               start_datetime=datetime(2018, 4, 1, 13, 15),
                                               end_datetime=datetime(2018, 4, 1, 15, 45))
        self.res3.save()
        self.factory = APIRequestFactory()
        self.view = Reservations.as_view()

    def test_1(self):
        request = self.factory.get("/pools/")
        force_authenticate(request=request, user=self.user1, token=self.key1)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
