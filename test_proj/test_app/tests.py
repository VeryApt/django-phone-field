from django.contrib import admin
from django.db import connection
from django.forms import Form, modelform_factory
from django.template import Context, Template
from django.test import TestCase
from phone_field import PhoneNumber
from phone_field.forms import PhoneFormField
from .models import TestModel, TestModelOptional


PARSING_TESTS = [
    (
        '4151234567',
        'simple',
        {
            'cleaned': '+14151234567', 'formatted': '(415) 123-4567', 'base_number': '+14151234567',
            'base_number_fmt': '(415) 123-4567', 'is_E164': True, 'is_standard': True, 'is_usa': True
        }
    ),
    (
        '(415) 123-4567',
        'already formatted',
        {
            'cleaned': '+14151234567', 'formatted': '(415) 123-4567', 'base_number': '+14151234567',
            'base_number_fmt': '(415) 123-4567', 'is_E164': True, 'is_standard': True, 'is_usa': True
        }
    ),
    (
        '(415) 123-4567, press 44',
        'already formatted with valid extensions',
        {
            'cleaned': '+14151234567x44', 'formatted': '(415) 123-4567, press 44', 'base_number': '+14151234567',
            'base_number_fmt': '(415) 123-4567', 'is_E164': False, 'is_standard': True, 'is_usa': True
        }
    ),
    (
        ' (415).123 - 4567 ',
        'messy formatted',
        {
            'cleaned': '+14151234567', 'formatted': '(415) 123-4567', 'base_number': '+14151234567',
            'base_number_fmt': '(415) 123-4567', 'is_E164': True, 'is_standard': True, 'is_usa': True
        }
    ),
    (
        ' (415).123 - 4567 x 44',
        'messy formatted with extension',
        {
            'cleaned': '+14151234567x44', 'formatted': '(415) 123-4567, press 44', 'base_number': '+14151234567',
            'base_number_fmt': '(415) 123-4567', 'is_E164': False, 'is_standard': True, 'is_usa': True
        }
    ),
    (
        '+44 (0)20-1234-3000',
        'international/unsupported',
        {
            'cleaned': '+44 (0)20-1234-3000', 'formatted': '+44 (0)20-1234-3000', 'base_number': '+44 (0)20-1234-3000',
            'base_number_fmt': '+44 (0)20-1234-3000', 'is_E164': False, 'is_standard': False, 'is_usa': False
        }
    )
]


#https://github.com/django/django/blob/master/tests/modeladmin/tests.py
class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


class TestFormRequired(Form):
    phone = PhoneFormField()


class TestFormOptional(Form):
    phone = PhoneFormField(required=False)


class ParsingTest(TestCase):
    def test_parsing(self):
        for input_str, label, attrs in PARSING_TESTS:
            ph = PhoneNumber(input_str)
            for key, val in attrs.items():
                self.assertEqual(getattr(ph, key), val, msg=label)


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


class ModelFormTest(TestCase):
    def test_modelform_rendering(self):
        Form = modelform_factory(TestModel, fields=('phone',))
        obj = TestModel(phone='415 123 4567 x 88')
        f = Form(instance=obj)
        expected = '<tr><th><label for="id_phone_0">Phone:</label></th><td><input type="text" name="phone_0" ' \
                   'value="(415) 123-4567" size="13" required id="id_phone_0" />\n\n&nbsp;&nbsp;ext.&nbsp;&nbsp;' \
                   '<input type="text" name="phone_1" value="88" size="4" id="id_phone_1" /></td></tr>'
        self.assertEqual(str(f), expected)

    def test_modelform_saving(self):
        Form = modelform_factory(TestModel, fields=('phone',))
        f = Form({'phone_0': '415.123.4567', 'phone_1': '88'})
        self.assertTrue(f.is_valid())
        obj = f.save()
        self.assertIsInstance(obj.phone, PhoneNumber)
        self.assertEqual(str(obj.phone), '(415) 123-4567, press 88')


class OptionalModelFormTest(TestCase):
    def test_modelform_rendering(self):
        Form = modelform_factory(TestModelOptional, fields=('phone',))
        obj = TestModelOptional(phone='415 123 4567 x 88')
        f = Form(instance=obj)
        expected = '<tr><th><label for="id_phone_0">Phone:</label></th><td><input type="text" name="phone_0" ' \
                   'value="(415) 123-4567" size="13" id="id_phone_0" />\n\n&nbsp;&nbsp;ext.&nbsp;&nbsp;' \
                   '<input type="text" name="phone_1" value="88" size="4" id="id_phone_1" /></td></tr>'
        self.assertEqual(str(f), expected)

    def test_modelform_empty(self):
        Form = modelform_factory(TestModelOptional, fields=('name', 'phone'))
        f = Form({'name': 'Ted', 'phone_0': '', 'phone_1': ''})
        self.assertTrue(f.is_valid())
        obj = f.save()
        self.assertEqual(obj.phone, '')


class AdminFormTest(TestCase):
    def setUp(self):
        self.site = admin.AdminSite()
        self.request = MockRequest()
        self.request.user = MockSuperUser()

    def test_admin_rendering(self):
        ma = admin.ModelAdmin(TestModel, self.site)
        obj = TestModel(phone='415 123 4567 x 88')
        Form = ma.get_form(self.request)
        f = Form(instance=obj)
        expected = '<tr><th><label for="id_phone_0">Phone:</label></th><td><input type="text" name="phone_0" ' \
                   'value="(415) 123-4567" size="13" required id="id_phone_0" />\n\n&nbsp;&nbsp;ext.&nbsp;&nbsp;' \
                   '<input type="text" name="phone_1" value="88" size="4" id="id_phone_1" /></td></tr>'
        self.assertEqual(str(f), expected)


class ModelTest(TestCase):
    def test_storage_retrieval(self):
        obj = TestModel(phone='(415) 123-4567 x 88')
        obj.save()

        # Test raw value
        with connection.cursor() as c:
            c.execute("SELECT phone FROM test_app_testmodel WHERE id={}".format(obj.pk))
            r = c.fetchone()
            self.assertEqual(r[0], '+14151234567x88', msg='Raw DB value mismatch')

        # Test Django attributes
        obj.refresh_from_db()
        self.assertIsInstance(obj.phone, PhoneNumber)
        self.assertEqual(str(obj.phone), '(415) 123-4567, press 88')

    def test_field_attrs(self):
        self.assertEqual(TestModel._meta.get_field('phone').max_length, 31)

