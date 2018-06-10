import json
from datetime import datetime

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Pool, Reservation, ExpirableToken
from .views import PoolsList, SingleReservation, Reservations, MailView


# Create your tests here.


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

        canceled = Reservation.objects.create(pool_id=self.pool.id, user_id=self.user1.id, slot_count=20,
                                              start_datetime=datetime(2018, 4, 1, 17, 00),
                                              end_datetime=datetime(2018, 4, 1, 18, 00), is_canceled=True)
        canceled.save()

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

    def test_get_wrong_format(self):
        data = {"pool_id": "id1", "slot_count": "abc"}
        request = self.factory.post("/pools/", data=data, format='json')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEqual(status.HTTP_400_BAD_REQUEST, data.status_code)


class SingleReservationDeleteTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(
            pool_id="id1", displayName="name1", maximumCount=10,
            enabled=True, description="desc1")
        self.pool.save()

        self.user = User.objects.create_user(username="user", password="test", email="testmail@mail.mail")
        self.user.save()
        token = ExpirableToken.objects.create(user=self.user, key=123123123123)
        token.save()
        self.key = token.key
        self.factory = APIRequestFactory()
        self.view = SingleReservation.as_view()

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
        reservation = Reservation.objects.get(id=res_id)
        self.assertTrue(reservation.is_canceled)

    def test_delete(self):
        total_res = 5
        reservation_id = [self.create_reservation() for _ in range(total_res)]

        response = self.get_response(reservation_id[0])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.check_if_is_deleted(reservation_id[0])

        for i in range(1, total_res):
            reservation = Reservation.objects.get(id=reservation_id[i])
            self.assertFalse(reservation.is_canceled)

    def test_double_delete(self):
        res_id = self.create_reservation()
        response = self.get_response(res_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.check_if_is_deleted(res_id)
        response = self.get_response(res_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.check_if_is_deleted(res_id)

    def test_never_existed(self):
        res_id = self.create_reservation()
        self.assertEqual(len(Reservation.objects.filter(id=res_id + 1)), 0)
        response = self.get_response(res_id + 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReservationsGetTest(TestCase):
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
        self.res2 = Reservation.objects.create(pool=self.pool2, user=self.user1, slot_count=2,
                                               start_datetime=datetime(2018, 4, 1, 13, 15),
                                               end_datetime=datetime(2018, 4, 1, 15, 45))
        self.res2.save()
        self.res3 = Reservation.objects.create(pool=self.pool2, user=self.user2, slot_count=4,
                                               start_datetime=datetime(2018, 4, 1, 13, 15),
                                               end_datetime=datetime(2018, 4, 1, 15, 45))
        self.res3.save()
        self.res4 = Reservation.objects.create(pool=self.pool2, user=self.user1, slot_count=1,
                                               start_datetime=datetime(2018, 4, 1, 16, 00),
                                               end_datetime=datetime(2018, 4, 1, 16, 30))
        self.res4.save()

        canceled = Reservation.objects.create(pool=self.pool2, user=self.user1, slot_count=1,
                                              start_datetime=datetime(2018, 4, 1, 16, 00),
                                              end_datetime=datetime(2018, 4, 1, 16, 30), is_canceled=True)
        canceled.save()

        self.factory = APIRequestFactory()
        self.view = Reservations.as_view()

    def test_no_param(self):
        request = self.factory.get("/pools/")
        force_authenticate(request=request, user=self.user1, token=self.key1)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        res = json.loads(data.content.decode())["reservations"]
        self.assertEqual(len(res), 3)
        self.assertTrue(res[0]["pool_id"] == "id1" and res[0]["slot_count"] == 5
                        and res[0]["start_datetime"] == "2018-04-01 11:15:00"
                        and res[0]["end_datetime"] == "2018-04-01 12:45:00")
        self.assertTrue(res[1]["pool_id"] == "id2" and res[1]["slot_count"] == 2
                        and res[1]["start_datetime"] == "2018-04-01 13:15:00"
                        and res[1]["end_datetime"] == "2018-04-01 15:45:00")
        self.assertTrue(res[2]["pool_id"] == "id2" and res[2]["slot_count"] == 1
                        and res[2]["start_datetime"] == "2018-04-01 16:00:00"
                        and res[2]["end_datetime"] == "2018-04-01 16:30:00")

    def test_param_start(self):
        request = self.factory.get("/pools/?start=2018-04-01 12:30:00")
        force_authenticate(request=request, user=self.user1, token=self.key1)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        res = json.loads(data.content.decode())["reservations"]
        self.assertEqual(len(res), 2)
        self.assertTrue(res[0]["pool_id"] == "id2" and res[0]["slot_count"] == 2
                        and res[0]["start_datetime"] == "2018-04-01 13:15:00"
                        and res[0]["end_datetime"] == "2018-04-01 15:45:00")
        self.assertTrue(res[1]["pool_id"] == "id2" and res[1]["slot_count"] == 1
                        and res[1]["start_datetime"] == "2018-04-01 16:00:00"
                        and res[1]["end_datetime"] == "2018-04-01 16:30:00")

    def test_param_end(self):
        request = self.factory.get("/pools/?end=2018-04-01 12:50:00")
        force_authenticate(request=request, user=self.user1, token=self.key1)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        res = json.loads(data.content.decode())["reservations"]
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]["pool_id"] == "id1" and res[0]["slot_count"] == 5
                        and res[0]["start_datetime"] == "2018-04-01 11:15:00"
                        and res[0]["end_datetime"] == "2018-04-01 12:45:00")

    def test_param_start_end(self):
        request = self.factory.get("/pools/?start=2018-04-01 12:30:00&end=2018-04-01 15:50:00")
        force_authenticate(request=request, user=self.user1, token=self.key1)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        res = json.loads(data.content.decode())["reservations"]
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]["pool_id"] == "id2" and res[0]["slot_count"] == 2
                        and res[0]["start_datetime"] == "2018-04-01 13:15:00"
                        and res[0]["end_datetime"] == "2018-04-01 15:45:00")

    def test_param_id(self):
        request = self.factory.get("/pools/?pid=id2")
        force_authenticate(request=request, user=self.user1, token=self.key1)
        data = self.view(request).render()
        self.assertEquals(status.HTTP_200_OK, data.status_code)
        res = json.loads(data.content.decode())["reservations"]
        self.assertEqual(len(res), 2)
        self.assertTrue(res[0]["pool_id"] == "id2" and res[0]["slot_count"] == 2
                        and res[0]["start_datetime"] == "2018-04-01 13:15:00"
                        and res[0]["end_datetime"] == "2018-04-01 15:45:00")
        self.assertTrue(res[1]["pool_id"] == "id2" and res[1]["slot_count"] == 1
                        and res[1]["start_datetime"] == "2018-04-01 16:00:00"
                        and res[1]["end_datetime"] == "2018-04-01 16:30:00")


class ReservationPostTest(TestCase):
    def setUp(self):
        self.pool = Pool.objects.create(pool_id="id1", displayName="name1", maximumCount=10,
                                        enabled=True, description="desc1")
        self.pool.save()
        self.user = User.objects.create_user(username="user1", password="testtesttest1", email="testmail1@mail.mail")
        self.user.save()
        token = ExpirableToken.objects.create(user=self.user, key=123123123123)
        token.save()
        self.key = token.key
        self.factory = APIRequestFactory()
        self.view = Reservations.as_view()

    def test_post_correct(self):
        file_text = '''"pool_id","start_date","end_date","start_time","end_time","slot_count","peroid"
"id1","2018-04-01","2018-04-01","12:00:00","14:15:00",2,0
"id1","2018-04-01","2018-04-01","13:00:00","17:00:00",3,0
'''
        file = SimpleUploadedFile('reservations.csv', file_text.encode())
        request = self.factory.post("/reservations/", data={'reservations': file}, format='multipart')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEqual(status.HTTP_201_CREATED, data.status_code)
        res = list(Reservation.objects.filter(pool=self.pool))
        self.assertEqual(len(res), 2)
        self.assertTrue(res[0].pool == self.pool and res[0].start_datetime == datetime(2018, 4, 1, 12, 00)
                        and res[0].end_datetime == datetime(2018, 4, 1, 14, 15) and res[0].slot_count == 2)
        self.assertTrue(res[1].pool == self.pool and res[1].start_datetime == datetime(2018, 4, 1, 13, 00)
                        and res[1].end_datetime == datetime(2018, 4, 1, 17, 00) and res[0].slot_count == 2)

    def test_post_incorrect(self):
        file_text = '''"pool_id","start_date","end_date","start_time","end_time","slot_count","peroid"
"id1","2018-04-01","2018-04-01","14:15:00",2,0
"id1","2018-04-01","2018-04-01","13:00:00",32:11,3,-2
'''
        file = SimpleUploadedFile('reservations.csv', file_text.encode())
        request = self.factory.post("/reservations/", data={'reservations': file}, format='multipart')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEqual(status.HTTP_400_BAD_REQUEST, data.status_code)
        res = list(Reservation.objects.filter(pool=self.pool))
        self.assertEqual(len(res), 0)

    def test_post_period(self):
        file_text = '''"pool_id","start_date","end_date","start_time","end_time","slot_count","peroid"
"id1","2018-04-01","2018-04-07","14:10:00","15:00:00",2,1
'''
        file = SimpleUploadedFile('reservations.csv', file_text.encode())
        request = self.factory.post("/reservations/", data={'reservations': file}, format='multipart')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEqual(status.HTTP_201_CREATED, data.status_code)
        res = list(Reservation.objects.filter(pool=self.pool))
        self.assertEqual(len(res), 7)
        for i in range(len(res)):
            self.assertTrue(res[i].pool == self.pool and res[i].start_datetime == datetime(2018, 4, i + 1, 14, 10)
                            and res[i].end_datetime == datetime(2018, 4, i + 1, 15, 00)
                            and res[i].slot_count == 2)


class MailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test", is_active=True)
        self.user.save()
        self.superuser = User.objects.create_superuser(username="admin1", email="myemail@mail.mail",
                                                       password="pass1")
        self.superuser.save()
        token = ExpirableToken.objects.create(user=self.user, key=123123123123)
        token.save()
        self.key = token.key
        self.factory = APIRequestFactory()
        self.view = MailView.as_view()

    def test_send(self):
        request = self.factory.post("/mail/", {"content": 'some mail content'}, format='json')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEquals(data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PCOIPPM message')

    def test_no_content(self):
        request = self.factory.post("/mail/", {'xyz': 'aaa'}, format='json')
        force_authenticate(request=request, user=self.user, token=self.key)
        data = self.view(request).render()
        self.assertEquals(data.status_code, status.HTTP_400_BAD_REQUEST)
