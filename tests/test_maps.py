import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.geo.models import City
from apps.orders.models import Order, OrderStatusHistory
from apps.orders.routing import get_simulation_flow
from apps.services.models import Service, ServiceCategory

User = get_user_model()


class MapDataDisplayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )
        self.sender_city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        self.recipient_city = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31, country='RU',
        )
        self.order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.sender_city, recipient_address=self.recipient_city,
            service=self.service,
        )

    def test_track_page_returns_200(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_coordinates_present_in_context(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertContains(response, '55.75')
        self.assertContains(response, '37.62')
        self.assertContains(response, '59.93')
        self.assertContains(response, '30.31')

    def test_sender_coordinates_correct(self):
        self.assertEqual(self.order.sender_address.latitude, 55.75)
        self.assertEqual(self.order.sender_address.longitude, 37.62)

    def test_recipient_coordinates_correct(self):
        self.assertEqual(self.order.recipient_address.latitude, 59.93)
        self.assertEqual(self.order.recipient_address.longitude, 30.31)

    def test_map_markers_in_html(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('#3b82f6', html)
        self.assertIn('#10b981', html)
        self.assertIn('new maplibregl.Marker', html)

    def test_route_variables_in_html(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('senderLng, senderLat', html)
        self.assertIn('recipientLng, recipientLat', html)

    def test_api_tracking_returns_virtual_location(self):
        response = self.client.get(
            reverse('orders:api_track', args=[self.order.tracking_number])
        )
        data = json.loads(response.content)
        self.assertIn('current_location', data)
        loc = data['current_location']
        self.assertIn('lat', loc)
        self.assertIn('lng', loc)
        self.assertIn('progress', loc)

    def test_map_variables_are_valid_numbers(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('isFinite(senderLat)', html)
        self.assertIn('isFinite(recipientLat)', html)

    def test_international_route_has_different_countries(self):
        intl_sender = City.objects.create(
            name='Beijing', latitude=39.90, longitude=116.40, country='CN',
        )
        intl_recipient = City.objects.create(
            name='Berlin', latitude=52.52, longitude=13.40, country='DE',
        )
        intl_order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Hans', recipient_phone='+49301234567',
            cargo_description='Docs', weight=2,
            sender_address=intl_sender, recipient_address=intl_recipient,
            service=self.service,
        )
        self.assertNotEqual(intl_sender.country, intl_recipient.country)
        flow = get_simulation_flow(intl_order)
        self.assertIn('customs_clearance', flow)


class MapEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )

    def test_order_without_cities_shows_fallback(self):
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            service=self.service,
        )
        response = self.client.get(
            reverse('orders:track', args=[order.tracking_number])
        )
        self.assertContains(response, 'senderCity = false')
        self.assertContains(response, 'recipientCity = false')

    def test_order_without_recipient_city_shows_fallback(self):
        sender = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=sender,
            service=self.service,
        )
        response = self.client.get(
            reverse('orders:track', args=[order.tracking_number])
        )
        self.assertContains(response, 'recipientCity = false')

    def test_order_without_sender_city_shows_fallback(self):
        recipient = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31, country='RU',
        )
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            recipient_address=recipient,
            service=self.service,
        )
        response = self.client.get(
            reverse('orders:track', args=[order.tracking_number])
        )
        self.assertContains(response, 'senderCity = false')


class MapDomesticInternationalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )

    def test_domestic_route_markers(self):
        moscow = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        spb = City.objects.create(name='SPB', latitude=59.93, longitude=30.31, country='RU')
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=moscow, recipient_address=spb,
            service=self.service,
        )
        response = self.client.get(
            reverse('orders:track', args=[order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('55.75', html)
        self.assertIn('37.62', html)
        self.assertIn('59.93', html)
        self.assertIn('30.31', html)
        self.assertIn('#3b82f6', html)
        self.assertIn('#10b981', html)

    def test_international_route_markers(self):
        moscow = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        berlin = City.objects.create(name='Berlin', latitude=52.52, longitude=13.40, country='DE')
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Hans', recipient_phone='+49301234567',
            cargo_description='Docs', weight=2,
            sender_address=moscow, recipient_address=berlin,
            service=self.service,
        )
        response = self.client.get(
            reverse('orders:track', args=[order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('55.75', html)
        self.assertIn('37.62', html)
        self.assertIn('52.52', html)
        self.assertIn('13.4', html)
        self.assertIn('#3b82f6', html)
        self.assertIn('#10b981', html)


class MapCreationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )

    def test_create_page_shows_map_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('orders:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Moscow')
        self.assertContains(response, 'latitude')