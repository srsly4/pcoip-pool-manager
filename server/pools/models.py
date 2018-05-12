# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
        return sum([reservation.slot_count for reservation in Reservation.objects.filter(pool_id=self.id)
                   .filter(end_datetime__gt=start, start_datetime__lt=end)])

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


class PoolData(models.Model):
    file = models.FileField()
