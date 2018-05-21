# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytz
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Pool(models.Model):
    """
    Model equivalent for one pool of virtual machines
    """
    pool_id = models.CharField(max_length=50)
    displayName = models.CharField(max_length=100)
    maximumCount = models.PositiveSmallIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    description = models.TextField(default="")

    def calculate_already_reserved_slots(self, start, end):
        """
        Counts number of slots already taken
        :param start: Datetime of beginning of reservation
        :param end: Datetime of finish of reservation
        :return: Number of slots already reserved
        """
        reservations = list(Reservation.objects
                            .filter(pool=self)
                            .filter(start_datetime__lt=end)
                            .filter(end_datetime__gt=start))
        all_times = [r.start_datetime for r in reservations] + [r.end_datetime for r in reservations] + [start, end]
        all_times.sort()
        max_used = 0
        for i in range(0, len(all_times) - 1):
            used = 0
            for r in reservations:
                if not (r.start_datetime > all_times[i + 1] or r.end_datetime < all_times[i]):
                    used += r.slot_count
            if used > max_used:
                max_used = used
        return max_used

    def can_place_reservation(self, number_of_slots, start, end):
        """
        Checks if reservation for given
        :param start: Datetime of beginning of reservation
        :param end: Datetime of finish of reservation
        :param number_of_slots: Number of slots user would like to reserve
        :return: True if the reservation is possible to place, else False
        """
        return self.maximumCount - self.calculate_already_reserved_slots(start, end) >= number_of_slots


class Reservation(models.Model):
    """
    Stores single reservation; is related to :model:'pools.Pool' and :model:'django.contrib.auth.models.User'
    """
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot_count = models.PositiveSmallIntegerField(default=0)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
