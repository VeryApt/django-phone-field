from django.db import models
from phone_field import PhoneField


class TestModel(models.Model):
    phone = PhoneField()
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)


class TestModelOptional(models.Model):
    name = models.CharField(max_length=31)
    phone = PhoneField(blank=True)


class TestModelBlankNull(models.Model):
    phone = PhoneField(blank=True, null=True)
