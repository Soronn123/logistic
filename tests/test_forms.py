from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.forms import CalculatorForm, ContactForm, TrackingForm
from apps.core.models import ContactMessage
from apps.geo.models import City
from apps.orders.forms import OrderForm
from apps.orders.models import Order
from apps.services.models import AdditionalService, Service, ServiceCategory
from apps.users.forms import (
    LoginForm, PasswordChangeForm, ProfileForm, RegisterForm, TicketForm, TicketMessageForm,
)
from apps.users.models import Ticket

User = get_user_model()


class ContactFormTest(TestCase):
    def test_valid_data(self):
        form = ContactForm(data={
            'name': 'Test User', 'email': 'test@example.com',
            'subject': 'Test Subject', 'message': 'Test message body',
        })
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('subject', form.errors)
        self.assertIn('message', form.errors)

    def test_invalid_email(self):
        form = ContactForm(data={
            'name': 'Test', 'email': 'not-an-email',
            'subject': 'Subject', 'message': 'Message',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_phone_optional(self):
        form = ContactForm(data={
            'name': 'Test', 'email': 'test@example.com',
            'subject': 'Subject', 'message': 'Message',
        })
        self.assertTrue(form.is_valid())

    def test_saves_to_db(self):
        form = ContactForm(data={
            'name': 'Test', 'email': 'test@example.com',
            'phone': '+79991234567', 'subject': 'Subject', 'message': 'Message',
        })
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsInstance(obj, ContactMessage)
        self.assertEqual(obj.name, 'Test')


class TrackingFormTest(TestCase):
    def test_valid_tracking_number(self):
        form = TrackingForm(data={'tracking_number': 'BK-ABC123DEF'})
        self.assertTrue(form.is_valid())

    def test_blank_tracking_number(self):
        form = TrackingForm(data={'tracking_number': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('tracking_number', form.errors)

    def test_long_tracking_number(self):
        form = TrackingForm(data={'tracking_number': 'A' * 21})
        self.assertFalse(form.is_valid())


class CalculatorFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )

    def test_valid_data(self):
        form = CalculatorForm(data={
            'from_city': self.city.pk, 'to_city': self.city.pk, 'weight': '10.00',
        })
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form = CalculatorForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('from_city', form.errors)
        self.assertIn('to_city', form.errors)
        self.assertIn('weight', form.errors)

    def test_negative_weight(self):
        form = CalculatorForm(data={
            'from_city': self.city.pk, 'to_city': self.city.pk, 'weight': '-5',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_weight(self):
        form = CalculatorForm(data={
            'from_city': self.city.pk, 'to_city': self.city.pk, 'weight': 'abc',
        })
        self.assertFalse(form.is_valid())


class LoginFormTest(TestCase):
    def test_form_has_email_field(self):
        form = LoginForm()
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)


class RegisterFormTest(TestCase):
    def test_valid_data(self):
        form = RegisterForm(data={
            'email': 'new@example.com', 'username': 'newuser',
            'password1': 'StrongPass1!', 'password2': 'StrongPass1!',
            'first_name': 'New', 'last_name': 'User',
        })
        self.assertTrue(form.is_valid())

    def test_passwords_dont_match(self):
        form = RegisterForm(data={
            'email': 'new@example.com', 'username': 'newuser',
            'password1': 'StrongPass1!', 'password2': 'DifferentPass1!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_blank_email(self):
        form = RegisterForm(data={
            'email': '', 'username': 'newuser',
            'password1': 'StrongPass1!', 'password2': 'StrongPass1!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user(
            username='existing', email='existing@example.com', password='test1234',
        )
        form = RegisterForm(data={
            'email': 'existing@example.com', 'username': 'newuser',
            'password1': 'StrongPass1!', 'password2': 'StrongPass1!',
        })
        self.assertFalse(form.is_valid())


class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )

    def test_valid_data(self):
        form = ProfileForm(data={
            'first_name': 'Updated', 'last_name': 'User',
            'email': 'test@example.com', 'language': 'ru', 'theme': 'light',
        }, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        User.objects.create_user(
            username='other', email='other@example.com', password='test1234',
        )
        form = ProfileForm(data={
            'first_name': 'Test', 'email': 'other@example.com',
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_blank_email(self):
        form = ProfileForm(data={'email': ''}, instance=self.user)
        self.assertFalse(form.is_valid())


class PasswordChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='oldpass123',
        )

    def test_valid_data(self):
        form = PasswordChangeForm(
            user=self.user,
            data={
                'old_password': 'oldpass123',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123',
            },
        )
        self.assertTrue(form.is_valid())

    def test_wrong_old_password(self):
        form = PasswordChangeForm(
            user=self.user,
            data={
                'old_password': 'wrongpass',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('old_password', form.errors)

    def test_passwords_dont_match(self):
        form = PasswordChangeForm(
            user=self.user,
            data={
                'old_password': 'oldpass123',
                'new_password1': 'newpass123',
                'new_password2': 'different456',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

    def test_password_too_short(self):
        form = PasswordChangeForm(
            user=self.user,
            data={
                'old_password': 'oldpass123',
                'new_password1': 'short',
                'new_password2': 'short',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

    def test_save_updates_password(self):
        form = PasswordChangeForm(
            user=self.user,
            data={
                'old_password': 'oldpass123',
                'new_password1': 'newpass123',
                'new_password2': 'newpass123',
            },
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))


class TicketFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )

    def test_valid_data(self):
        form = TicketForm(data={
            'subject': 'Test Issue', 'priority': 'high', 'message': 'Help needed',
        })
        self.assertTrue(form.is_valid())

    def test_blank_subject(self):
        form = TicketForm(data={'subject': '', 'priority': 'medium', 'message': 'Help'})
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

    def test_saves_with_message(self):
        form = TicketForm(data={
            'subject': 'Issue', 'priority': 'low', 'message': 'Details',
        })
        self.assertTrue(form.is_valid())
        ticket = form.save(commit=False)
        ticket.created_by = self.user
        ticket.save()
        self.assertEqual(ticket.subject, 'Issue')


class TicketMessageFormTest(TestCase):
    def test_valid_data(self):
        form = TicketMessageForm(data={'message': 'Test reply'})
        self.assertTrue(form.is_valid())

    def test_blank_message(self):
        form = TicketMessageForm(data={'message': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)


class OrderFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        cls.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )
        cls.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')
        cls.service = Service.objects.create(
            category=cls.category, name='Test Service', slug='test-service',
        )
        cls.additional = AdditionalService.objects.create(
            name='Insurance', slug='insurance', price=500,
        )

    def test_valid_data(self):
        form = OrderForm(data={
            'sender_name': 'John Doe', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane Doe', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Electronics', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertTrue(form.is_valid())

    def test_blank_sender_name(self):
        form = OrderForm(data={
            'sender_name': '', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('sender_name', form.errors)

    def test_blank_recipient_name(self):
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': self.city.pk,
            'recipient_name': '', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('recipient_name', form.errors)

    def test_invalid_phone_format(self):
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '12345',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('sender_phone', form.errors)

    def test_blank_phone(self):
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('sender_phone', form.errors)

    def test_missing_sender_city(self):
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': '',
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('sender_address', form.errors)

    def test_missing_recipient_city(self):
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': '',
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('recipient_address', form.errors)

    def test_optional_fields_not_required(self):
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
        }, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.fields['volume'].required)
        self.assertFalse(form.fields['declared_value'].required)
        self.assertFalse(form.fields['sender_email'].required)
        self.assertFalse(form.fields['recipient_email'].required)

    def test_prefills_user_data(self):
        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.save()
        form = OrderForm(user=self.user)
        self.assertEqual(form.fields['sender_name'].initial, 'Test User')

    def test_additional_services_queryset(self):
        form = OrderForm(user=self.user)
        self.assertTrue(form.fields['additional_services'].queryset.exists())

    def test_door_service_with_branch_delivery(self):
        Branch = __import__('apps.geo.models', fromlist=['Branch']).Branch
        Branch.objects.create(
            city=self.city, branch_type='pickup_point',
            address='Branch St', latitude=55.75, longitude=37.62,
            has_pickup=True,
        )
        door_service = AdditionalService.objects.create(
            name='Door Delivery', slug='door', price=1000, is_door_service=True,
        )
        form = OrderForm(data={
            'sender_name': 'John', 'sender_phone': '+7 (999) 123-45-67',
            'sender_address': self.city.pk,
            'recipient_name': 'Jane', 'recipient_phone': '+7 (999) 765-43-21',
            'recipient_address': self.city.pk,
            'cargo_description': 'Stuff', 'weight': '5.00',
            'service': self.service.pk,
            'additional_services': [door_service.pk],
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('additional_services', form.errors)