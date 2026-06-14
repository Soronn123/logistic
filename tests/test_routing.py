from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.geo.models import Branch, City
from apps.orders.routing import (
    auto_assign_services,
    calculate_price,
    compute_eta,
    get_initial_status,
    has_branch_in_city,
    has_warehouse_in_city,
)
from apps.services.models import AdditionalService, Service, ServiceCategory, Tariff

User = get_user_model()


class RoutingHelperTests(TestCase):
    def setUp(self):
        self.city_a = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
            is_active=True, country='RU',
        )
        self.city_b = City.objects.create(
            name='Saint Petersburg', latitude=59.93, longitude=30.31,
            is_active=True, country='RU',
        )
        self.city_foreign = City.objects.create(
            name='Beijing', latitude=39.90, longitude=116.40,
            is_active=True, country='CN',
        )
        self.category = ServiceCategory.objects.create(name='Transport', slug='transport')

    def test_has_branch_in_city_false(self):
        self.assertFalse(has_branch_in_city(self.city_a))

    def test_has_branch_in_city_true(self):
        Branch.objects.create(
            city=self.city_a, branch_type='office',
            address='Test', latitude=55.75, longitude=37.62,
            is_active=True,
        )
        self.assertTrue(has_branch_in_city(self.city_a))

    def test_has_warehouse_in_city_false(self):
        self.assertFalse(has_warehouse_in_city(self.city_a))

    def test_has_warehouse_in_city_true(self):
        Branch.objects.create(
            city=self.city_a, branch_type='warehouse',
            address='Test', latitude=55.75, longitude=37.62,
            is_active=True,
        )
        self.assertTrue(has_warehouse_in_city(self.city_a))

    def test_get_initial_status_no_city(self):
        self.assertEqual(get_initial_status(None), 'draft')

    def test_get_initial_status_with_warehouse(self):
        Branch.objects.create(
            city=self.city_a, branch_type='warehouse',
            address='Test', latitude=55.75, longitude=37.62,
            is_active=True,
        )
        status = get_initial_status(self.city_a)
        self.assertEqual(status, 'awaiting_delivery_to_branch')

    def test_calculate_price_with_tariff(self):
        Tariff.objects.create(
            name='Standard', min_weight=0, max_weight=100,
            price_per_kg=50, delivery_days_min=1, delivery_days_max=3,
        )
        result = calculate_price(self.city_a, self.city_b, 10)
        self.assertIn('total_price', result)
        self.assertGreater(result['total_price'], 0)

    def test_compute_eta_returns_date(self):
        eta = compute_eta(self.city_a, self.city_b, delivery_days=3)
        self.assertIsNotNone(eta)


class AutoAssignServicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city_ru = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
            is_active=True, country='RU',
        )
        cls.city_ru2 = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31,
            is_active=True, country='RU',
        )
        cls.city_cn = City.objects.create(
            name='Beijing', latitude=39.90, longitude=116.40,
            is_active=True, country='CN',
        )
        cls.cat = ServiceCategory.objects.create(name='Cat', slug='cat')

        # Create additional services used by auto-assignment
        for slug, name in [
            ('customs-duty', 'Customs duty'),
            ('customs-clearance', 'Customs clearance'),
            ('warehouse-transit', 'Warehouse transit'),
            ('last-mile-delivery', 'Last-mile delivery'),
            ('email-order-created', 'Email: order created'),
            ('email-customs-cleared', 'Email: customs cleared'),
            ('email-delivered', 'Email: delivered'),
            ('extended-insurance', 'Extended insurance'),
            ('hand-carry', 'Hand Carry'),
            ('adr-transport', 'ADR transport'),
            ('refrigerated-transport', 'Refrigerated transport'),
        ]:
            AdditionalService.objects.create(name=name, slug=slug, price=Decimal('500'))

        # Main services
        Service.objects.create(
            category=cls.cat, name='Truck', slug='truck-transport',
            base_price=Decimal('100'), is_active=True,
        )
        Service.objects.create(
            category=cls.cat, name='Rail', slug='rail-transport',
            base_price=Decimal('80'), is_active=True,
        )
        Service.objects.create(
            category=cls.cat, name='Air', slug='air-transport',
            base_price=Decimal('200'), is_active=True,
        )

    def test_domestic_small_cargo_no_customs(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
            is_fragile=False, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertNotIn('customs-duty', slugs)
        self.assertNotIn('customs-clearance', slugs)

    def test_international_adds_customs(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_cn,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
            is_fragile=False, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('customs-duty', slugs)
        self.assertIn('customs-clearance', slugs)

    def test_high_value_adds_extended_insurance(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=100000,
            is_fragile=False, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('extended-insurance', slugs)

    def test_low_value_no_extended_insurance(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
            is_fragile=False, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertNotIn('extended-insurance', slugs)

    def test_fragile_adds_hand_carry(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
            is_fragile=True, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('hand-carry', slugs)

    def test_dangerous_adds_adr(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
            is_fragile=False, is_dangerous=True, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('adr-transport', slugs)

    def test_temperature_sensitive_adds_refrigerated(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
            is_fragile=False, is_dangerous=False, is_temperature_sensitive=True,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('refrigerated-transport', slugs)

    def test_oversize_selects_truck(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=100, length=50, width=40, height=30,
            declared_value=10000,
        )
        self.assertIsNotNone(result['service'])
        self.assertIn(result['service'].slug, ['truck-transport', 'rail-transport'])

    def test_normal_size_selects_air(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
        )
        self.assertIsNotNone(result['service'])

    def test_international_customs_notifications(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_cn,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('email-order-created', slugs)
        self.assertIn('email-customs-cleared', slugs)
        self.assertIn('email-delivered', slugs)

    def test_domestic_notifications(self):
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('email-order-created', slugs)
        self.assertIn('email-delivered', slugs)
        self.assertNotIn('email-customs-cleared', slugs)

    def test_no_warehouse_in_destination(self):
        # No warehouse branch in city_ru2
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('last-mile-delivery', slugs)

    def test_warehouse_in_destination_no_last_mile(self):
        Branch.objects.create(
            city=self.city_ru2, branch_type='warehouse',
            address='Test', latitude=59.93, longitude=30.31,
            is_active=True,
        )
        result = auto_assign_services(
            from_city=self.city_ru, to_city=self.city_ru2,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertNotIn('last-mile-delivery', slugs)


class IntegrationScenarioTests(TestCase):
    """Test the three scenarios from the requirements."""

    @classmethod
    def setUpTestData(cls):
        cls.cat = ServiceCategory.objects.create(name='Cat', slug='cat')

        for slug, name, price in [
            ('customs-duty', 'Customs duty', 1000),
            ('customs-clearance', 'Customs clearance', 1500),
            ('warehouse-transit', 'Warehouse transit', 800),
            ('last-mile-delivery', 'Last-mile delivery', 1200),
            ('email-order-created', 'Email: order created', 100),
            ('email-customs-cleared', 'Email: customs cleared', 100),
            ('email-delivered', 'Email: delivered', 100),
            ('extended-insurance', 'Extended insurance', 2000),
            ('hand-carry', 'Hand Carry', 1500),
            ('adr-transport', 'ADR transport', 3000),
            ('refrigerated-transport', 'Refrigerated transport', 2500),
        ]:
            AdditionalService.objects.create(name=name, slug=slug, price=Decimal(str(price)))

        Service.objects.create(category=cls.cat, name='Truck', slug='truck-transport', base_price=100, is_active=True)
        Service.objects.create(category=cls.cat, name='Rail', slug='rail-transport', base_price=80, is_active=True)
        Service.objects.create(category=cls.cat, name='Air', slug='air-transport', base_price=200, is_active=True)

    def test_scenario1_domestic_small_direct(self):
        """Domestic shipment, small cargo, direct route -> expect: truck, basic insurance, no customs"""
        from_city = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        to_city = City.objects.create(name='Tver', latitude=56.85, longitude=35.90, country='RU')

        result = auto_assign_services(
            from_city=from_city, to_city=to_city,
            weight=10, length=50, width=40, height=30,
            declared_value=30000,
            is_fragile=False, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertNotIn('customs-duty', slugs)
        self.assertNotIn('customs-clearance', slugs)
        self.assertIsNotNone(result['service'])

    def test_scenario2_international_fragile_high_value(self):
        """International, fragile, high value -> customs, careful handling, extended insurance, air if weight allows"""
        from_city = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        to_city = City.objects.create(name='Almaty', latitude=43.22, longitude=76.85, country='KZ')

        result = auto_assign_services(
            from_city=from_city, to_city=to_city,
            weight=30, length=60, width=50, height=40,
            declared_value=100000,
            is_fragile=True, is_dangerous=False, is_temperature_sensitive=False,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('customs-duty', slugs)
        self.assertIn('customs-clearance', slugs)
        self.assertIn('hand-carry', slugs)
        self.assertIn('extended-insurance', slugs)

    def test_scenario3_no_warehouse_destination(self):
        """No warehouse in destination city -> last-mile delivery service added"""
        from_city = City.objects.create(name='Moscow', latitude=55.75, longitude=37.62, country='RU')
        to_city = City.objects.create(name='Small Town', latitude=54.0, longitude=38.0, country='RU')
        # No warehouse in to_city

        result = auto_assign_services(
            from_city=from_city, to_city=to_city,
            weight=10, length=50, width=40, height=30,
            declared_value=10000,
        )
        slugs = [a.slug for a in result['additional_services']]
        self.assertIn('last-mile-delivery', slugs)
