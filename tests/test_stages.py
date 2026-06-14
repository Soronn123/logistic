from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.geo.models import City
from apps.orders.models import Order, OrderStatusHistory
from apps.orders.routing import (
    get_next_statuses, get_simulation_flow, simulate_next_status,
)
from apps.services.models import Service, ServiceCategory

User = get_user_model()


class StageSequenceLogicTests(TestCase):
    def test_domestic_flow_skips_customs_clearance(self):
        moscow = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        spb = City.objects.create(name='SPB', latitude=59.93, longitude=30.31, country='RU')
        from apps.orders.models import Order

        flow = get_simulation_flow(
            Order(sender_address=moscow, recipient_address=spb)
        )
        self.assertNotIn('customs_clearance', flow)
        self.assertEqual(flow, ['draft', 'confirmed', 'awaiting_courier', 'picked_up', 'in_transit', 'at_warehouse', 'out_for_delivery', 'delivered'])

    def test_international_flow_includes_customs_clearance(self):
        moscow = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        berlin = City.objects.create(name='Berlin', latitude=52.52, longitude=13.40, country='DE')
        from apps.orders.models import Order

        flow = get_simulation_flow(
            Order(sender_address=moscow, recipient_address=berlin)
        )
        self.assertIn('customs_clearance', flow)
        self.assertEqual(flow, ['draft', 'confirmed', 'awaiting_courier', 'picked_up', 'in_transit', 'customs_clearance', 'at_warehouse', 'out_for_delivery', 'delivered'])

    def test_stages_cannot_be_skipped_domestic(self):
        for current, allowed in [
            ('draft', ['confirmed']),
            ('confirmed', ['picked_up']),
            ('picked_up', ['in_transit']),
            ('in_transit', ['at_warehouse', 'out_for_delivery']),
            ('at_warehouse', ['out_for_delivery']),
            ('out_for_delivery', ['delivered']),
            ('delivered', []),
        ]:
            next_statuses = get_next_statuses(current, is_international=False)
            self.assertEqual(next_statuses, allowed, f'Failed for {current} -> {allowed}')

    def test_stages_cannot_be_skipped_international(self):
        for current, allowed in [
            ('draft', ['confirmed']),
            ('confirmed', ['picked_up']),
            ('picked_up', ['in_transit']),
            ('in_transit', ['customs_clearance', 'at_warehouse', 'out_for_delivery']),
            ('customs_clearance', ['at_warehouse', 'out_for_delivery']),
            ('at_warehouse', ['out_for_delivery']),
            ('out_for_delivery', ['delivered']),
            ('delivered', []),
        ]:
            next_statuses = get_next_statuses(current, is_international=True)
            self.assertEqual(next_statuses, allowed, f'Failed for {current} -> {allowed}')

    def test_invalid_transition_returns_empty(self):
        self.assertEqual(get_next_statuses('delivered'), [])
        self.assertEqual(get_next_statuses('cancelled'), [])

    def test_simulate_next_status_returns_correct_order(self):
        moscow = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        spb = City.objects.create(name='SPB', latitude=59.93, longitude=30.31, country='RU')
        cat = ServiceCategory.objects.create(name='Cat', slug='cat')
        svc = Service.objects.create(category=cat, name='Svc', slug='svc')
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        order = Order.objects.create(
            user=user, sender_name='A', sender_phone='+79991234567',
            recipient_name='B', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=moscow, recipient_address=spb,
            service=svc, status='draft',
        )

        expected = ['confirmed', 'awaiting_courier', 'picked_up', 'in_transit', 'at_warehouse', 'out_for_delivery', 'delivered']
        for next_status in expected:
            result = simulate_next_status(order)
            self.assertIsNotNone(result)
            self.assertEqual(result, next_status)
            order.status = next_status
            order.save()

        self.assertIsNone(simulate_next_status(order))


class StageTransitionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.moscow = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        self.spb = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31, country='RU',
        )
        self.cat = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.svc = Service.objects.create(category=self.cat, name='Svc', slug='svc')
        self.order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.moscow, recipient_address=self.spb,
            service=self.svc, status='draft',
        )

    def test_updated_at_changes_on_transition(self):
        original_updated = self.order.updated_at
        self.order.status = 'confirmed'
        self.order.save()
        self.order.refresh_from_db()
        self.assertGreater(self.order.updated_at, original_updated)

    def test_status_history_created_on_transition(self):
        self.order.status = 'confirmed'
        self.order.save()
        OrderStatusHistory.objects.create(
            order=self.order, status='confirmed',
            changed_by=self.user, comment='Test transition',
        )
        self.assertEqual(self.order.status_history.count(), 1)
        entry = self.order.status_history.first()
        self.assertEqual(entry.status, 'confirmed')
        self.assertEqual(entry.changed_by, self.user)

    def test_status_history_timestamps_ordered(self):
        statuses = ['draft', 'confirmed', 'picked_up', 'in_transit']
        for i, s in enumerate(statuses):
            OrderStatusHistory.objects.create(
                order=self.order, status=s,
                changed_by=self.user,
                timestamp=timezone.now() + timedelta(hours=i),
            )
        history = self.order.status_history.all().order_by('timestamp')
        self.assertEqual(history[0].status, 'draft')
        self.assertEqual(history[1].status, 'confirmed')
        self.assertEqual(history[2].status, 'picked_up')
        self.assertEqual(history[3].status, 'in_transit')


class StageUserFacingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.moscow = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        self.spb = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31, country='RU',
        )
        self.cat = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.svc = Service.objects.create(category=self.cat, name='Svc', slug='svc')
        self.order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.moscow, recipient_address=self.spb,
            service=self.svc, status='in_transit',
        )

    @override_settings(LANGUAGE_CODE='en')
    def test_current_stage_displayed_on_track_page(self):
        OrderStatusHistory.objects.create(
            order=self.order, status='in_transit',
            changed_by=self.user,
        )
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'In transit')

    @override_settings(LANGUAGE_CODE='en')
    def test_status_history_shown_on_track_page(self):
        statuses = ['draft', 'confirmed', 'picked_up', 'in_transit']
        for s in statuses:
            OrderStatusHistory.objects.create(
                order=self.order, status=s,
                changed_by=self.user,
                timestamp=timezone.now(),
            )
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)
        for s in statuses:
            label = dict(Order.Status.choices).get(s, s)
            self.assertContains(response, label)

    @override_settings(LANGUAGE_CODE='en')
    def test_track_page_shows_delivered_for_completed(self):
        self.order.status = 'delivered'
        self.order.actual_delivery_date = timezone.now().date()
        self.order.save()
        OrderStatusHistory.objects.create(
            order=self.order, status='delivered',
            changed_by=self.user,
        )
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertContains(response, 'Delivered')


@override_settings(LANGUAGE_CODE='en')
class StageFullHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.moscow = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        self.spb = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31, country='RU',
        )
        self.cat = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.svc = Service.objects.create(category=self.cat, name='Svc', slug='svc')
        self.order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.moscow, recipient_address=self.spb,
            service=self.svc, status='draft',
        )

    def test_full_stage_history_in_admin_detail(self):
        admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='admin123', is_staff=True, role='admin',
        )
        statuses = ['draft', 'confirmed', 'picked_up', 'in_transit', 'at_warehouse', 'out_for_delivery', 'delivered']
        for s in statuses:
            OrderStatusHistory.objects.create(
                order=self.order, status=s, changed_by=admin,
                timestamp=timezone.now(),
            )
        self.client.force_login(admin)
        response = self.client.get(
            reverse('dashboard:order_detail', args=[self.order.pk])
        )
        self.assertEqual(response.status_code, 200)
        for s in statuses:
            self.assertContains(response, dict(Order.Status.choices).get(s, s))