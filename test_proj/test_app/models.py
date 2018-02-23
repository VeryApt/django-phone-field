from django.db import models
from phone_field import PhoneField


class TestModel(models.Model):
    phone = PhoneField()


class TestModelOptional(models.Model):
    name = models.CharField(max_length=31)
    phone = PhoneField(blank=True)

