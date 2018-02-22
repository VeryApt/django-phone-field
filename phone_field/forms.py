from django import forms
from .phone_number import PhoneNumber


class PhoneWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        attrs = attrs or {}
        first_attrs = {'size': 13}
        second_attrs = {'size': 4}
        first_attrs.update(attrs)
        second_attrs.update(attrs)
        _widgets = (
            forms.TextInput(attrs=first_attrs),
            forms.TextInput(attrs=second_attrs)
        )
        super(PhoneWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if isinstance(value, PhoneNumber):
            return value.base_number_fmt, 'x'.join(value.extensions)
        return value, ''

    def format_output(self, rendered_widgets):
        return '{}&nbsp;&nbsp;ext.&nbsp;&nbsp;{}'.format(rendered_widgets[0], rendered_widgets[1])

    def value_from_datadict(self, data, files, name):
        parts = super(PhoneWidget, self).value_from_datadict(data, files, name)
        return 'x'.join(p for p in parts if p)


class PhoneFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = PhoneWidget
        super(PhoneFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        val = super(PhoneFormField, self).to_python(value)
        if val:
            val = PhoneNumber(val)
        return val
