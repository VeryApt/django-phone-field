from django.forms import ModelForm, CharField
from .models import TestModel


class RequiredInputsForm(ModelForm):
    other_field = CharField()

    class Meta:
        model = TestModel
        fields = ['phone', 'first_name', 'last_name']
