import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.models import (
    ContactMessage, ContentPage, FAQ, NewsItem, Promotion, Review, Tender, Vacancy,
)
from apps.documents.models import AccountingRequest, Document
from apps.geo.models import Branch, BranchImage, City
from apps.orders.models import Order, OrderStatusHistory
from apps.partners.models import Banner, IframeModule, PartnerApplication
from apps.services.models import AdditionalService, Service, ServiceCategory, Tariff
from apps.users.models import ContactTemplate, DeliveryTemplate, Ticket, TicketMessage, Transaction

User = get_user_model()


class CoreURLTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )
        self.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', slug='test-service',
        )
        self.tariff = Tariff.objects.create(
            name='Standard', min_weight=0, max_weight=100,
            price_per_kg=10, delivery_days_min=1, delivery_days_max=5,
        )
        self.additional_service = AdditionalService.objects.create(
            name='Insurance', slug='insurance', price=500,
        )
        self.tender = Tender.objects.create(
            title='Test Tender', slug='test-tender',
            description='Desc', deadline=timezone.now() + timedelta(days=30),
        )
        self.promotion = Promotion.objects.create(
            title='Test Promo', slug='test-promo',
            short_description='Short', full_description='Full',
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=30),
        )
        self.news = NewsItem.objects.create(
            title='Test News', slug='test-news',
            short_text='Short', full_text='Full',
            published_at=timezone.now(),
        )
        self.vacancy = Vacancy.objects.create(
            title='Test Vacancy', slug='test-vacancy',
            department='IT', short_description='Short',
            full_description='Full', requirements='Req',
            city=self.city,
        )
        self.review = Review.objects.create(
            author_name='Test User', text='Great!', rating=5, is_approved=True,
        )
        self.faq = FAQ.objects.create(
            question='Test Q', answer='Test A',
        )
        self.content_page = ContentPage.objects.create(
            slug='about-company', title='About Company',
            content='<p>Content</p>', page_type='about', is_published=True,
        )
        self.branch = Branch.objects.create(
            city=self.city, branch_type='office',
            address='123 Test St', latitude=55.75, longitude=37.62,
        )

    def test_home_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/core/home.html')

    def test_about_returns_200(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

    def test_news_list_returns_200(self):
        response = self.client.get(reverse('core:news_list'))
        self.assertEqual(response.status_code, 200)

    def test_news_detail_returns_200(self):
        response = self.client.get(reverse('core:news_detail', args=[self.news.slug]))
        self.assertEqual(response.status_code, 200)

    def test_news_detail_404(self):
        response = self.client.get(reverse('core:news_detail', args=['non-existent']))
        self.assertEqual(response.status_code, 404)

    def test_reviews_returns_200(self):
        response = self.client.get(reverse('core:reviews'))
        self.assertEqual(response.status_code, 200)

    def test_vacancies_returns_200(self):
        response = self.client.get(reverse('core:vacancies'))
        self.assertEqual(response.status_code, 200)

    def test_vacancy_detail_returns_200(self):
        response = self.client.get(reverse('core:vacancy_detail', args=[self.vacancy.slug]))
        self.assertEqual(response.status_code, 200)

    def test_vacancy_detail_404(self):
        response = self.client.get(reverse('core:vacancy_detail', args=['non-existent']))
        self.assertEqual(response.status_code, 404)

    def test_contact_get_returns_200(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_post_creates_message(self):
        data = {
            'name': 'Test', 'email': 'test@example.com',
            'subject': 'Test Subject', 'message': 'Test message body',
        }
        response = self.client.post(reverse('core:contact'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email='test@example.com').exists())

    def test_faq_returns_200(self):
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)

    def test_tenders_returns_200(self):
        response = self.client.get(reverse('core:tenders'))
        self.assertEqual(response.status_code, 200)

    def test_tender_detail_returns_200(self):
        response = self.client.get(reverse('core:tender_detail', args=[self.tender.slug]))
        self.assertEqual(response.status_code, 200)

    def test_promotions_returns_200(self):
        response = self.client.get(reverse('core:promotions'))
        self.assertEqual(response.status_code, 200)

    def test_promotion_detail_returns_200(self):
        response = self.client.get(reverse('core:promotion_detail', args=[self.promotion.slug]))
        self.assertEqual(response.status_code, 200)

    def test_directions_returns_200(self):
        response = self.client.get(reverse('core:directions'))
        self.assertEqual(response.status_code, 200)

    def test_calculator_get_returns_200(self):
        response = self.client.get(reverse('core:calculator'))
        self.assertEqual(response.status_code, 200)

    def test_calculator_post_valid(self):
        data = {'from_city': self.city.pk, 'to_city': self.city.pk, 'weight': '10.00'}
        response = self.client.post(reverse('core:calculator'), data)
        self.assertEqual(response.status_code, 200)

    def test_delivery_times_returns_200(self):
        response = self.client.get(reverse('core:delivery_times'))
        self.assertEqual(response.status_code, 200)

    def test_create_order_redirects(self):
        response = self.client.get(reverse('core:create_order'))
        self.assertEqual(response.status_code, 302)

    def test_track_get_returns_200(self):
        response = self.client.get(reverse('core:track'))
        self.assertEqual(response.status_code, 200)

    def test_tariffs_returns_200(self):
        response = self.client.get(reverse('core:tariffs'))
        self.assertEqual(response.status_code, 200)

    def test_mobile_app_returns_200(self):
        response = self.client.get(reverse('core:mobile_app'))
        self.assertEqual(response.status_code, 200)

    def test_brand_assets_returns_200(self):
        response = self.client.get(reverse('core:brand_assets'))
        self.assertEqual(response.status_code, 200)

    def test_press_returns_200(self):
        response = self.client.get(reverse('core:press'))
        self.assertEqual(response.status_code, 200)

    def test_warehouse_returns_200(self):
        response = self.client.get(reverse('core:warehouse'))
        self.assertEqual(response.status_code, 200)

    def test_info_page_returns_200(self):
        response = self.client.get(reverse('core:info_page', args=[self.content_page.slug]))
        self.assertEqual(response.status_code, 200)

    def test_info_page_404(self):
        response = self.client.get(reverse('core:info_page', args=['non-existent']))
        self.assertEqual(response.status_code, 404)


class UsersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )

    def test_login_returns_200(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_valid(self):
        data = {'username': 'test@example.com', 'password': 'testpass123'}
        response = self.client.post(reverse('users:login'), data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_register_returns_200(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_post_valid(self):
        data = {
            'email': 'new@example.com', 'username': 'newuser',
            'password1': 'StrongPass1!', 'password2': 'StrongPass1!',
            'first_name': 'New', 'last_name': 'User',
        }
        response = self.client.post(reverse('users:register'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_profile_requires_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)

    def test_settings_requires_login(self):
        response = self.client.get(reverse('users:settings'))
        self.assertEqual(response.status_code, 302)

    def test_settings_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:settings'))
        self.assertEqual(response.status_code, 200)

    def test_balance_requires_login(self):
        response = self.client.get(reverse('users:balance'))
        self.assertEqual(response.status_code, 302)

    def test_balance_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:balance'))
        self.assertEqual(response.status_code, 200)

    def test_balance_topup_redirects_on_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:balance_topup'))
        self.assertEqual(response.status_code, 302)

    def test_balance_topup_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('users:balance_topup'), {'amount': '1000'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 1000)

    def test_tickets_requires_login(self):
        response = self.client.get(reverse('users:tickets'))
        self.assertEqual(response.status_code, 302)

    def test_tickets_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:tickets'))
        self.assertEqual(response.status_code, 200)

    def test_ticket_create_requires_login(self):
        response = self.client.get(reverse('users:ticket_create'))
        self.assertEqual(response.status_code, 302)

    def test_ticket_create_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:ticket_create'))
        self.assertEqual(response.status_code, 200)

    def test_ticket_create_post(self):
        self.client.force_login(self.user)
        data = {'subject': 'Test Issue', 'priority': 'high', 'message': 'Help me'}
        response = self.client.post(reverse('users:ticket_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Ticket.objects.filter(subject='Test Issue').exists())

    def test_orders_requires_login(self):
        response = self.client.get(reverse('users:orders'))
        self.assertEqual(response.status_code, 302)

    def test_orders_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:orders'))
        self.assertEqual(response.status_code, 200)


class ServicesURLTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', slug='test-service',
        )
        self.tariff = Tariff.objects.create(
            name='Standard', min_weight=0, max_weight=100,
            price_per_kg=10, delivery_days_min=1, delivery_days_max=5,
        )
        self.additional = AdditionalService.objects.create(
            name='Extra', slug='extra', price=100,
        )

    def test_list_returns_200(self):
        response = self.client.get(reverse('services:list'))
        self.assertEqual(response.status_code, 200)

    def test_category_detail_returns_200(self):
        response = self.client.get(reverse('services:category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)

    def test_service_detail_returns_200(self):
        response = self.client.get(
            reverse('services:detail', args=[self.category.slug, self.service.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_additional_returns_200(self):
        response = self.client.get(reverse('services:additional'))
        self.assertEqual(response.status_code, 200)

    def test_tariffs_returns_200(self):
        response = self.client.get(reverse('services:tariffs'))
        self.assertEqual(response.status_code, 200)

    def test_service_detail_404(self):
        response = self.client.get(
            reverse('services:detail', args=['bad-cat', 'bad-svc'])
        )
        self.assertEqual(response.status_code, 404)


class OrdersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )
        self.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', slug='test-service',
        )
        self.order = Order.objects.create(
            user=self.user,
            sender_name='Sender', sender_phone='+79991234567',
            recipient_name='Recipient', recipient_phone='+79997654321',
            cargo_description='Stuff', weight=10,
            sender_address=self.city, recipient_address=self.city,
            service=self.service,
        )

    def test_create_requires_login(self):
        response = self.client.get(reverse('orders:create'))
        self.assertEqual(response.status_code, 302)

    def test_create_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('orders:create'))
        self.assertEqual(response.status_code, 200)

    def test_track_returns_200(self):
        response = self.client.get(
            reverse('orders:track', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_track_404(self):
        response = self.client.get(
            reverse('orders:track', args=['NONEXISTENT'])
        )
        self.assertEqual(response.status_code, 404)

    def test_door_delivery_returns_200(self):
        response = self.client.get(
            reverse('orders:door_delivery', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_request_changes_returns_200(self):
        response = self.client.get(
            reverse('orders:request_changes', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)

    def test_create_order_post(self):
        self.client.force_login(self.user)
        data = {
            'sender_name': 'Test Sender', 'sender_phone': '+7 (999) 111-22-33',
            'sender_email': 'sender@test.com',
            'sender_address': self.city.pk, 'sender_address_detail': 'Street 1',
            'recipient_name': 'Test Recipient', 'recipient_phone': '+7 (999) 444-55-66',
            'recipient_email': 'recipient@test.com',
            'recipient_address': self.city.pk, 'recipient_address_detail': 'Street 2',
            'cargo_description': 'Test cargo', 'weight': '5.00',
            'service': self.service.pk,
        }
        response = self.client.post(reverse('orders:create'), data, follow=True)
        self.assertEqual(response.status_code, 200)


class GeoURLTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62, is_active=True,
        )
        self.branch = Branch.objects.create(
            city=self.city, branch_type='office',
            address='123 Test St', latitude=55.75, longitude=37.62,
        )

    def test_branches_returns_200(self):
        response = self.client.get(reverse('geo:branches'))
        self.assertEqual(response.status_code, 200)

    def test_city_branches_returns_200(self):
        response = self.client.get(
            reverse('geo:city_branches', args=[self.city.name])
        )
        self.assertEqual(response.status_code, 200)

    def test_city_branches_404(self):
        response = self.client.get(
            reverse('geo:city_branches', args=['nonexistent-city'])
        )
        self.assertEqual(response.status_code, 404)


class PartnersURLTests(TestCase):
    def setUp(self):
        self.banner = Banner.objects.create(
            title='Test Banner', image='banners/test.jpg', link='https://example.com',
            start_date=timezone.now(), end_date=timezone.now() + timedelta(days=30),
            placement='header',
        )
        self.iframe = IframeModule.objects.create(
            name='Test Widget', embed_code='<iframe></iframe>',
        )

    def test_overview_returns_200(self):
        response = self.client.get(reverse('partners:overview'))
        self.assertEqual(response.status_code, 200)

    def test_apply_returns_200(self):
        response = self.client.get(reverse('partners:apply'))
        self.assertEqual(response.status_code, 200)

    def test_apply_post_creates_application(self):
        data = {
            'company_name': 'Test Corp', 'contact_person': 'John',
            'email': 'john@test.com', 'phone': '+79991234567',
        }
        response = self.client.post(reverse('partners:apply'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PartnerApplication.objects.filter(company_name='Test Corp').exists())

    def test_iframe_returns_200(self):
        response = self.client.get(reverse('partners:iframe'))
        self.assertEqual(response.status_code, 200)

    def test_banners_returns_200(self):
        response = self.client.get(reverse('partners:banners'))
        self.assertEqual(response.status_code, 200)


class DocumentsURLTests(TestCase):
    def setUp(self):
        self.doc = Document.objects.create(
            title='Test Doc', category='contracts',
            file='documents/test.pdf',
        )

    def test_list_returns_200(self):
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)

    def test_category_returns_200(self):
        response = self.client.get(reverse('documents:category', args=['contracts']))
        self.assertEqual(response.status_code, 200)


class DashboardURLTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='admin123', is_staff=True, role='admin',
        )
        self.regular_user = User.objects.create_user(
            username='regular', email='regular@example.com',
            password='regular123',
        )
        self.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )
        self.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', slug='test-service',
        )
        self.branch = Branch.objects.create(
            city=self.city, branch_type='office',
            address='123 Test St', latitude=55.75, longitude=37.62,
        )

    def test_login_returns_200(self):
        response = self.client.get(reverse('dashboard:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_valid(self):
        data = {'username': 'admin@example.com', 'password': 'admin123'}
        response = self.client.post(reverse('dashboard:login'), data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_requires_staff(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_home_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_redirects_for_non_staff(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertIn(response.status_code, [302, 403])

    def test_users_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:users'))
        self.assertEqual(response.status_code, 200)

    def test_user_create_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:user_create'))
        self.assertEqual(response.status_code, 200)

    def test_user_create_post(self):
        self.client.force_login(self.admin_user)
        data = {
            'email': 'newstaff@example.com', 'username': 'newstaff',
            'first_name': 'New', 'last_name': 'Staff', 'role': 'manager',
            'language': 'ru', 'theme': 'light', 'balance': '0',
        }
        response = self.client.post(reverse('dashboard:user_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='newstaff@example.com').exists())

    def test_orders_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:orders'))
        self.assertEqual(response.status_code, 200)

    def test_tickets_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:tickets'))
        self.assertEqual(response.status_code, 200)

    def test_services_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:services'))
        self.assertEqual(response.status_code, 200)

    def test_service_create_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:service_create'))
        self.assertEqual(response.status_code, 200)

    def test_service_create_post(self):
        self.client.force_login(self.admin_user)
        data = {
            'category': self.category.pk, 'name': 'New Service',
            'name_en': '', 'slug': 'new-service',
            'short_description': '', 'description': '',
            'icon': 'fa-box', 'base_price': '1000.00',
            'price_unit': 'per kg', 'sort_order': '0',
        }
        response = self.client.post(reverse('dashboard:service_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Service.objects.filter(slug='new-service').exists())

    def test_content_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:content'))
        self.assertEqual(response.status_code, 200)

    def test_branches_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:branches'))
        self.assertEqual(response.status_code, 200)

    def test_branch_create_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:branch_create'))
        self.assertEqual(response.status_code, 200)

    def test_branch_create_post(self):
        self.client.force_login(self.admin_user)
        data = {
            'city': self.city.pk, 'branch_type': 'warehouse',
            'address': '456 New St', 'latitude': '55.0', 'longitude': '37.0',
        }
        response = self.client.post(reverse('dashboard:branch_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Branch.objects.filter(address='456 New St').exists())

    def test_documents_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:documents'))
        self.assertEqual(response.status_code, 200)

    def test_partners_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:partners'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:contacts'))
        self.assertEqual(response.status_code, 200)

    def test_settings_returns_200_for_staff(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:settings'))
        self.assertEqual(response.status_code, 200)

    def test_user_edit_returns_200(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('dashboard:user_edit', args=[self.regular_user.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_service_edit_returns_200(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('dashboard:service_edit', args=[self.service.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_branch_edit_returns_200(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('dashboard:branch_edit', args=[self.branch.pk])
        )
        self.assertEqual(response.status_code, 200)


class OrderAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )
        self.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', slug='test-service',
        )
        self.order = Order.objects.create(
            user=self.user,
            sender_name='Sender', sender_phone='+79991234567',
            recipient_name='Recipient', recipient_phone='+79997654321',
            cargo_description='Stuff', weight=10,
            sender_address=self.city, recipient_address=self.city,
            service=self.service, status='in_transit',
        )
        self.client.force_login(self.user)

    def test_api_status_post(self):
        response = self.client.post(
            reverse('orders:api_status', args=[self.order.tracking_number]),
            {'status': 'at_warehouse'},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'at_warehouse')

    def test_api_status_invalid_transition(self):
        response = self.client.post(
            reverse('orders:api_status', args=[self.order.tracking_number]),
            {'status': 'delivered'},
        )
        self.assertEqual(response.status_code, 400)

    def test_api_track_get(self):
        response = self.client.get(
            reverse('orders:api_track', args=[self.order.tracking_number])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['tracking_number'], self.order.tracking_number)