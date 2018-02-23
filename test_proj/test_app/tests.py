from django.db import connection
from django.forms import Form, CharField
from django.template import Context, Template
from django.test import TestCase
from phone_field import PhoneField, PhoneNumber
from phone_field.forms import PhoneFormField
from .models import TestModel


class TestFormRequired(Form):
    phone = PhoneFormField()


class TestFormOptional(Form):
    phone = PhoneFormField(required=False)


class RenderingTest(TestCase):
    def test_native(self):
        t = Template(r'{{ ph }}')
        out = t.render(Context({'ph': PhoneNumber('4151234567')}))
        self.assertEqual(out, '(415) 123-4567')

    def test_phone_filter(self):
        t = Template(r'{% load phone %}{{ ph|phone }}')
        out = t.render(Context({'ph': '415.123.4567'}))
        self.assertEqual(out, '(415) 123-4567')

    def test_raw_filter_native(self):
        t = Template(r'{% load phone %}{{ ph|raw_phone }}')
        out = t.render(Context({'ph': PhoneNumber('415-123-4567')}))
        self.assertEqual(out, '+14151234567')

    def test_raw_filter_fallback(self):
        t = Template(r'{% load phone %}{{ ph|raw_phone }}')
        out = t.render(Context({'ph': '415-123-4567'}))
        self.assertEqual(out, '4151234567')


class RequiredFormTest(TestCase):
    def test_form_rendering(self):
        f = TestFormRequired(initial={'phone': PhoneNumber('415.123.4567 x 12')})
        expected = '<tr><th><label for="id_phone_0">Phone:</label></th><td><input type="text" name="phone_0" ' \
                   'value="(415) 123-4567" size="13" required id="id_phone_0" />\n\n&nbsp;&nbsp;ext.&nbsp;&nbsp;' \
                   '<input type="text" name="phone_1" value="12" size="4" id="id_phone_1" /></td></tr>'
        self.assertEqual(str(f), expected)

    def test_form_empty(self):
        f = TestFormRequired({})
        self.assertFalse(f.is_valid())

    def test_form_normal(self):
        f = TestFormRequired({'phone_0': '415.123.4567'})
        self.assertTrue(f.is_valid())
        self.assertIsInstance(f.cleaned_data['phone'], PhoneNumber)
        self.assertEqual(str(f.cleaned_data['phone']), '(415) 123-4567')

    def test_form_extension(self):
        f = TestFormRequired({'phone_0': '415.123.4567', 'phone_1': '88'})
        self.assertTrue(f.is_valid())
        self.assertIsInstance(f.cleaned_data['phone'], PhoneNumber)
        self.assertEqual(str(f.cleaned_data['phone']), '(415) 123-4567, press 88')


class OptionalFormTest(TestCase):
    def test_form_rendering(self):
        f = TestFormOptional(initial={'phone': PhoneNumber('415.123.4567 x 12')})
        expected = '<tr><th><label for="id_phone_0">Phone:</label></th><td><input type="text" name="phone_0" ' \
                   'value="(415) 123-4567" size="13" id="id_phone_0" />\n\n&nbsp;&nbsp;ext.&nbsp;&nbsp;' \
                   '<input type="text" name="phone_1" value="12" size="4" id="id_phone_1" /></td></tr>'
        self.assertEqual(str(f), expected)

    def test_form_empty(self):
        f = TestFormOptional({})
        self.assertTrue(f.is_valid())

    def test_form_full(self):
        f = TestFormOptional({'phone_0': '415 123 4567', 'phone_1': '88'})
        self.assertTrue(f.is_valid())
        self.assertEqual(str(f.cleaned_data['phone']), '(415) 123-4567, press 88')


class ModelTest(TestCase):
    def _test_parsing(self, str_in, str_db, str_cleaned, str_fmt, str_base, str_base_fmt, is_E164, is_standard, 
                      is_usa):
        obj = TestModel(phone=str_in)
        obj.save()

        # Test raw value
        with connection.cursor() as c:
            c.execute("SELECT phone FROM test_app_testmodel WHERE id={}".format(obj.pk))
            r = c.fetchone()
            self.assertEqual(r[0], str_db, msg='Raw DB value mismatch')

        # Test Django attributes
        obj.refresh_from_db()
        self.assertIsInstance(obj.phone, PhoneNumber)
        self.assertEqual(obj.phone.cleaned, str_cleaned)
        self.assertEqual(str(obj.phone), str_fmt)
        self.assertEqual(obj.phone.base_number, str_base)
        self.assertEqual(obj.phone.base_number_fmt, str_base_fmt)
        self.assertEqual(obj.phone.is_E164, is_E164)
        self.assertEqual(obj.phone.is_standard, is_standard)
        self.assertEqual(obj.phone.is_usa, is_usa)

    def test_cleanest_phone(self):
        self._test_parsing('4151234567', '+14151234567', '+14151234567', '(415) 123-4567', '+14151234567',
                           '(415) 123-4567', True, True, True)

    def test_formatted_phone(self):
        self._test_parsing('(415) 123-4567', '+14151234567', '+14151234567', '(415) 123-4567', '+14151234567',
                           '(415) 123-4567', True, True, True)

    def test_messy_phone(self):
        self._test_parsing(' (415).123 - 4567 ', '+14151234567', '+14151234567', '(415) 123-4567', '+14151234567',
                           '(415) 123-4567', True, True, True)

    def test_extension(self):
        self._test_parsing(' (415).123 - 4567 x 44', '+14151234567x44', '+14151234567x44', '(415) 123-4567, press 44',
                           '+14151234567', '(415) 123-4567', False, True, True)

    def test_international(self):
        self._test_parsing('+44 (0)20-1234-3000', '+44 (0)20-1234-3000', '+44 (0)20-1234-3000',
                           '+44 (0)20-1234-3000', '+44 (0)20-1234-3000', '+44 (0)20-1234-3000', False, False, False)
