from django.db import models
from phone_field import PhoneField


class TestModel(models.Model):
    phone = PhoneField()
