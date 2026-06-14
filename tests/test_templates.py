import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.geo.models import City
from apps.orders.models import Order, OrderStatusHistory
from apps.services.models import AdditionalService, Service, ServiceCategory

User = get_user_model()


class OrderCreateTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
            balance=5000,
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU', is_active=True,
        )
        self.city2 = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31, country='RU', is_active=True,
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Express', slug='express',
            base_price=1000, price_unit='per kg', is_active=True,
        )
        self.addon = AdditionalService.objects.create(
            name='Insurance', slug='insurance', price=500, price_type='fixed', is_active=True,
        )
        self.client.force_login(self.user)

    def test_create_page_uses_correct_template(self):
        response = self.client.get(reverse('orders:create'))
        self.assertTemplateUsed(response, 'pages/orders/create.html')

    def test_create_page_returns_200(self):
        response = self.client.get(reverse('orders:create'))
        self.assertEqual(response.status_code, 200)

    def test_context_contains_cities(self):
        response = self.client.get(reverse('orders:create'))
        self.assertIn('cities', response.context)
        self.assertEqual(len(response.context['cities']), 2)

    def test_context_contains_services(self):
        response = self.client.get(reverse('orders:create'))
        self.assertIn('services', response.context)
        self.assertEqual(len(response.context['services']), 1)

    def test_context_contains_additional_services(self):
        response = self.client.get(reverse('orders:create'))
        self.assertIn('additional_services', response.context)
        self.assertEqual(len(response.context['additional_services']), 1)

    def test_context_contains_cities_json(self):
        response = self.client.get(reverse('orders:create'))
        self.assertIn('cities_json', response.context)
        data = json.loads(response.context['cities_json'])
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Moscow')
        self.assertEqual(data[1]['name'], 'SPB')

    def test_context_has_default_coordinates(self):
        response = self.client.get(reverse('orders:create'))
        self.assertEqual(response.context['default_lat'], 55.7558)
        self.assertEqual(response.context['default_lng'], 37.6173)

    def test_context_has_user_balance(self):
        response = self.client.get(reverse('orders:create'))
        self.assertEqual(response.context['user_balance'], 5000.0)

    def test_context_has_auto_service_slugs(self):
        response = self.client.get(reverse('orders:create'))
        self.assertIn('auto_service_slugs', response.context)
        slugs = response.context['auto_service_slugs']
        self.assertEqual(slugs['customs_duty'], 'customs-duty')
        self.assertEqual(slugs['extended_insurance'], 'extended-insurance')
        self.assertEqual(slugs['hand_carry'], 'hand-carry')

    def test_city_options_in_select(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Moscow', html)
        self.assertIn('SPB', html)
        self.assertIn('value="{}"'.format(self.city.id), html)
        self.assertIn('value="{}"'.format(self.city2.id), html)

    def test_service_radio_buttons_rendered(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Express', html)
        self.assertIn('value="{}"'.format(self.service.id), html)
        self.assertIn('name="service"', html)

    def test_additional_service_checkboxes_rendered(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Insurance', html)
        self.assertIn('value="{}"'.format(self.addon.id), html)
        self.assertIn('name="additional_services"', html)

    def test_form_has_csrf_token(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('csrfmiddlewaretoken', html)

    def test_form_has_required_fields(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('name="sender_name"', html)
        self.assertIn('name="sender_phone"', html)
        self.assertIn('name="sender_address"', html)
        self.assertIn('name="recipient_name"', html)
        self.assertIn('name="recipient_phone"', html)
        self.assertIn('name="recipient_address"', html)
        self.assertIn('name="cargo_description"', html)
        self.assertIn('name="weight"', html)
        self.assertIn('name="declared_value"', html)
        self.assertIn('name="sender_address_detail"', html)
        self.assertIn('name="recipient_address_detail"', html)

    def test_special_handling_checkboxes_rendered(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('name="is_fragile"', html)
        self.assertIn('name="is_dangerous"', html)
        self.assertIn('name="is_temperature_sensitive"', html)

    def test_map_container_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('id="order-map"', html)

    def test_progress_bar_steps_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Sender', html)
        self.assertIn('Recipient', html)
        self.assertIn('Cargo', html)
        self.assertIn('Services', html)
        self.assertIn('Confirm', html)

    def test_default_coordinates_in_json(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('55.7558', html)
        self.assertIn('37.6173', html)

    def test_navigation_buttons_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('x-show="step < 5"', html)

    def test_terms_checkbox_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('name="terms"', html)

    def test_auto_assignment_info_section_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Auto-assigned', html)

    def test_base_template_extended(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('<!doctype html>', html)

    def test_maplibre_stylesheet_loaded(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('maplibre-gl', html)
        self.assertIn('unpkg.com/maplibre-gl', html)

    def test_page_title_contains_create_word(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Baikal-Service', html)

    def test_dimension_fields_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('name="length"', html)
        self.assertIn('name="width"', html)
        self.assertIn('name="height"', html)

    def test_service_base_price_in_html(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('data-base-price', html)
        self.assertIn('1000', html)

    def test_additional_service_price_type_in_html(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('data-addon-price', html)
        self.assertIn('data-addon-price-type', html)

    def test_alpinejs_data_attribute_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('x-data="orderForm()"', html)

    def test_inline_script_block_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('function orderForm()', html)

    def test_form_action_to_create_url(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('action="{}"'.format(reverse('orders:create')), html)

    def test_save_as_template_button_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('saveTemplate', html)

    def test_fragile_option_description(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Fragile', html)
        self.assertIn('Hand Carry', html)

    def test_dangerous_option_description(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Dangerous goods', html)
        self.assertIn('ADR', html)

    def test_temperature_option_description(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Temperature-sensitive', html)
        self.assertIn('Refrigerated', html)

    def test_submit_button_has_alpine_binding(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('x-text="submitting', html)

    def test_back_button_has_x_show(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('x-show="step > 1"', html)

    def test_cities_json_serialized_properly(self):
        response = self.client.get(reverse('orders:create'))
        cities_json = response.context['cities_json']
        data = json.loads(cities_json)
        for entry in data:
            self.assertIn('id', entry)
            self.assertIn('name', entry)
            self.assertIn('latitude', entry)
            self.assertIn('longitude', entry)
            self.assertIn('country', entry)

    def test_select_city_has_empty_label(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('<option value="">', html)


class OrderCreateTemplateBalanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
            balance=0,
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU', is_active=True,
        )
        self.client.force_login(self.user)

    def test_balance_warning_shown_when_balance_zero(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Пополнить баланс', html)

    def test_balance_warning_link_to_topup(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn(reverse('users:balance_topup'), html)

    def test_no_balance_warning_when_balance_positive(self):
        self.user.balance = 5000
        self.user.save()
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertNotIn('Пополнить баланс', html)

    def test_no_balance_warning_when_balance_negative(self):
        self.user.balance = -100
        self.user.save()
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('Пополнить баланс', html)


class OrderCreateTemplateDeliveryTemplatesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
            balance=5000,
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU', is_active=True,
        )
        self.client.force_login(self.user)

    def test_delivery_templates_section_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('deliveryTemplates', html)

    def test_sender_templates_binding_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('senderTemplates', html)

    def test_recipient_templates_binding_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('recipientTemplates', html)

    def test_cargo_templates_binding_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('cargoTemplates', html)

    def test_quick_access_section_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('showQuickAccess', html)
        self.assertIn('loadDeliveryTemplate', html)

    def test_save_delivery_template_button_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('saveDeliveryTemplate', html)

    def test_save_cargo_template_button_present(self):
        response = self.client.get(reverse('orders:create'))
        html = response.content.decode()
        self.assertIn('saveCargoTemplate', html)


class OrderTrackTemplateTests(TestCase):
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
            service=self.service, status='confirmed',
            total_price=2500,
        )
        self.history = OrderStatusHistory.objects.create(
            order=self.order, status='confirmed',
            changed_by=self.user, comment='Order created',
        )

    def test_track_page_uses_correct_template(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertTemplateUsed(response, 'pages/orders/track.html')

    def test_track_page_returns_200(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_tracking_number_displayed(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(self.order.tracking_number, html)

    def test_status_badge_rendered(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(self.order.get_status_display(), html)

    def test_status_history_rendered(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Order created', html)

    def test_status_history_timestamp_rendered(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(str(self.history.timestamp.year), html)

    def test_route_info_displayed(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Moscow', html)
        self.assertIn('SPB', html)

    def test_delivery_info_weight_displayed(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(str(self.order.weight), html)
        self.assertIn('kg', html)

    def test_delivery_info_price_displayed(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(str(int(self.order.total_price)), html)

    def test_cargopickedup_button_shown_for_confirmable_status(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Груз забран', html)

    def test_confirm_delivery_button_shown_for_deliverable_status(self):
        self.client.force_login(self.user)
        self.order.status = 'out_for_delivery'
        self.order.save()
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Подтвердить доставку', html)

    def test_request_changes_link_shown_for_owner(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Запросить изменения', html)

    def test_request_changes_link_contains_url(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(
            reverse('orders:request_changes', args=[self.order.tracking_number]),
            html,
        )

    def test_request_changes_link_not_shown_for_anonymous(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertNotIn('Запросить изменения', html)

    def test_estimated_delivery_label_displayed(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Ожидаемая', html)

    def test_map_container_present(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('id="track-map"', html)

    def test_context_has_status_history(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertIn('status_history', response.context)
        self.assertEqual(response.context['status_history'].count(), 1)

    def test_sender_recipient_coordinates_in_html(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('55.75', html)
        self.assertIn('37.62', html)
        self.assertIn('59.93', html)
        self.assertIn('30.31', html)

    def test_track_page_shows_price_label(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Цена', html)

    def test_progress_bar_rendered(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Прогресс отправки', html)

    def test_delivery_info_section(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Информация о доставке', html)

    def test_action_buttons_section_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('/pickup/', html)
        self.assertIn('request-changes', html)

    def test_route_section(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Маршрут', html)

    def test_status_history_empty_message(self):
        order2 = Order.objects.create(
            user=self.user,
            sender_name='A', sender_phone='+79991234567',
            recipient_name='B', recipient_phone='+79997654321',
            cargo_description='Box', weight=1,
            sender_address=self.sender_city, recipient_address=self.recipient_city,
            service=self.service,
        )
        response = self.client.get(
            reverse('orders:track', args=[order2.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('История статусов недоступна', html)

    def test_maplibre_js_loaded(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('maplibregl.Map', html)
        self.assertIn('maplibregl.Marker', html)

    def test_sender_address_detail_rendered(self):
        self.order.sender_address_detail = 'Street 1'
        self.order.save()
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Street 1', html)

    def test_recipient_address_detail_rendered(self):
        self.order.recipient_address_detail = 'Street 2'
        self.order.save()
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Street 2', html)

    def test_cargo_description_in_track_page(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Box', html)


class OrderTrackTemplateStatusBadgeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )

    def test_delivered_status_displayed(self):
        order = Order.objects.create(
            user=self.user, sender_name='A', sender_phone='+79991234567',
            recipient_name='B', recipient_phone='+79997654321',
            cargo_description='Box', weight=1,
            sender_address=self.city, recipient_address=self.city,
            service=self.service, status='delivered',
        )
        response = self.client.get(reverse('orders:track', args=[order.tracking_number]))
        html = response.content.decode()
        self.assertIn(order.get_status_display(), html)

    def test_cancelled_status_displayed(self):
        order = Order.objects.create(
            user=self.user, sender_name='A', sender_phone='+79991234567',
            recipient_name='B', recipient_phone='+79997654321',
            cargo_description='Box', weight=1,
            sender_address=self.city, recipient_address=self.city,
            service=self.service, status='cancelled',
        )
        response = self.client.get(reverse('orders:track', args=[order.tracking_number]))
        html = response.content.decode()
        self.assertIn(order.get_status_display(), html)

    def test_in_transit_status_displayed(self):
        order = Order.objects.create(
            user=self.user, sender_name='A', sender_phone='+79991234567',
            recipient_name='B', recipient_phone='+79997654321',
            cargo_description='Box', weight=1,
            sender_address=self.city, recipient_address=self.city,
            service=self.service, status='in_transit',
        )
        response = self.client.get(reverse('orders:track', args=[order.tracking_number]))
        html = response.content.decode()
        self.assertIn(order.get_status_display(), html)

    def test_draft_status_displayed(self):
        order = Order.objects.create(
            user=self.user, sender_name='A', sender_phone='+79991234567',
            recipient_name='B', recipient_phone='+79997654321',
            cargo_description='Box', weight=1,
            sender_address=self.city, recipient_address=self.city,
            service=self.service, status='draft',
        )
        response = self.client.get(reverse('orders:track', args=[order.tracking_number]))
        html = response.content.decode()
        self.assertIn(order.get_status_display(), html)


class OrderTrackTemplateAddressFallbackTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )

    def test_no_sender_city_shows_fallback(self):
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
        html = response.content.decode()
        self.assertIn('senderCity = false', html)

    def test_no_recipient_city_shows_fallback(self):
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
        html = response.content.decode()
        self.assertIn('recipientCity = false', html)

    def test_no_cities_shows_fallback(self):
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
        html = response.content.decode()
        self.assertIn('senderCity = false', html)
        self.assertIn('recipientCity = false', html)


class TrackingLookupTemplateTests(TestCase):
    def test_lookup_page_returns_200(self):
        response = self.client.get(reverse('tracking_lookup'))
        self.assertEqual(response.status_code, 200)

    def test_lookup_page_uses_correct_template(self):
        response = self.client.get(reverse('tracking_lookup'))
        self.assertTemplateUsed(response, 'pages/orders/tracking_lookup.html')

    def test_lookup_form_has_input_field(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('name="tracking_number"', html)

    def test_lookup_form_has_submit_button(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('type="submit"', html)

    def test_lookup_form_action_to_tracking_lookup(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn(reverse('tracking_lookup'), html)

    def test_lookup_page_title(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('Отследить груз', html)

    def test_lookup_form_placeholder(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('трек-номер', html)
        self.assertIn('BK-', html)

    def test_lookup_page_has_steps_section(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('01', html)
        self.assertIn('02', html)
        self.assertIn('03', html)
        self.assertIn('04', html)

    def test_lookup_page_has_contact_link(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn(reverse('core:contact'), html)

    def test_lookup_page_has_help_text(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('Нужна помощь', html)

    def test_lookup_page_label_for_input(self):
        response = self.client.get(reverse('tracking_lookup'))
        html = response.content.decode()
        self.assertIn('for="tracking_number"', html)


class DoorDeliveryTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )
        self.order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.city, recipient_address=self.city,
            service=self.service,
        )

    def test_door_delivery_page_uses_correct_template(self):
        response = self.client.get(
            reverse('orders:door_delivery', args=[self.order.tracking_number])
        )
        self.assertTemplateUsed(response, 'pages/orders/door_delivery.html')

    def test_door_delivery_page_returns_200(self):
        response = self.client.get(
            reverse('orders:door_delivery', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_door_delivery_page_has_title(self):
        response = self.client.get(
            reverse('orders:door_delivery', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Доставка до двери', html)


class RequestChangesTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, country='RU',
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )
        self.order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.city, recipient_address=self.city,
            service=self.service,
        )
        self.client.force_login(self.user)

    def test_request_changes_uses_correct_template(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        self.assertTemplateUsed(response, 'pages/orders/request_changes.html')

    def test_request_changes_page_returns_200(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_request_changes_has_form(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('method="post"', html)
        self.assertIn('name="message"', html)
        self.assertIn('id="id_message"', html)

    def test_request_changes_has_csrf_token(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('csrfmiddlewaretoken', html)

    def test_request_changes_shows_order_summary(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Order Summary', html)
        self.assertIn(self.order.get_status_display(), html)
        self.assertIn('Moscow', html)

    def test_request_changes_shows_tracking_number(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn(self.order.tracking_number, html)

    def test_request_changes_has_back_link(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Back to tracking', html)
        self.assertIn(
            reverse('orders:track', args=[self.order.tracking_number]),
            html,
        )

    def test_request_changes_has_submit_button(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Submit Request', html)

    def test_request_changes_has_cancel_button(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Отмена', html)

    def test_request_changes_shows_previous_change_requests(self):
        OrderStatusHistory.objects.create(
            order=self.order, status=self.order.status,
            changed_by=self.user,
            comment='[Change Request] Please update address',
        )
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Previous Change Requests', html)
        self.assertIn('Please update address', html)

    def test_request_changes_hides_previous_requests_when_none(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertNotIn('text-lg font-semibold text-gray-900 dark:text-white mb-4">Previous Change Requests</h2>', html)

    def test_request_changes_comment_is_always_present(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('Previous Change Requests', html)

    def test_request_changes_context_contains_order(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'], self.order)

    def test_request_changes_context_contains_change_requests(self):
        OrderStatusHistory.objects.create(
            order=self.order, status=self.order.status,
            changed_by=self.user,
            comment='[Change Request] Test',
        )
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        self.assertIn('change_requests', response.context)
        self.assertEqual(response.context['change_requests'].count(), 1)

    def test_request_changes_textarea_placeholder(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('placeholder', html)
        self.assertIn('delivery address', html)

    def test_request_changes_form_method_post(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        html = response.content.decode()
        self.assertIn('method="post"', html)
        self.assertIn('name="message"', html)
