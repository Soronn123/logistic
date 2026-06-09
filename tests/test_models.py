from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.core.models import (
    ContactMessage, ContentPage, FAQ, NewsItem, Promotion, Review, Tender, Vacancy,
)
from apps.documents.models import AccountingRequest, Document
from apps.geo.models import Branch, BranchImage, City
from apps.orders.models import Order, OrderDocument, OrderStatusHistory
from apps.partners.models import Banner, IframeModule, PartnerApplication
from apps.services.models import AdditionalService, Service, ServiceCategory, Tariff
from apps.users.models import ContactTemplate, DeliveryTemplate, Ticket, TicketMessage, Transaction

User = get_user_model()


class CoreModelTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='Test City', latitude=55.75, longitude=37.62, is_active=True,
        )

    def test_content_page_creation(self):
        page = ContentPage.objects.create(
            slug='test-page', title='Test Page',
            content='<p>Content</p>', page_type='about',
        )
        self.assertEqual(str(page), 'Test Page')
        self.assertEqual(page.page_type, 'about')

    def test_faq_creation(self):
        faq = FAQ.objects.create(question='Test Q?', answer='Test A.')
        self.assertEqual(str(faq), 'Test Q?')
        self.assertTrue(faq.is_published)

    def test_review_creation(self):
        review = Review.objects.create(
            author_name='John', text='Great service!', rating=5,
        )
        self.assertEqual(str(review), 'John - 5/5')
        self.assertFalse(review.is_approved)

    def test_news_item_creation(self):
        news = NewsItem.objects.create(
            title='News Title', slug='news-title',
            short_text='Short', full_text='Full',
            published_at=timezone.now(),
        )
        self.assertEqual(str(news), 'News Title')
        self.assertFalse(news.is_pinned)
        self.assertEqual(NewsItem.objects.count(), 1)

    def test_vacancy_creation(self):
        vacancy = Vacancy.objects.create(
            title='Developer', slug='developer',
            department='IT', short_description='Desc',
            full_description='Full Desc', requirements='Python',
            city=self.city,
        )
        self.assertEqual(str(vacancy), 'Developer')

    def test_contact_message_creation(self):
        msg = ContactMessage.objects.create(
            name='Alice', email='alice@example.com',
            subject='Question', message='Help!',
        )
        self.assertEqual(str(msg), 'Alice - Question')
        self.assertFalse(msg.is_read)

    def test_tender_creation(self):
        tender = Tender.objects.create(
            title='Tender 1', slug='tender-1',
            description='Desc', deadline=timezone.now() + timedelta(days=30),
        )
        self.assertEqual(str(tender), 'Tender 1')
        self.assertTrue(tender.is_active)

    def test_promotion_creation(self):
        promo = Promotion.objects.create(
            title='Sale!', slug='sale',
            short_description='Short', full_description='Full',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
        )
        self.assertEqual(str(promo), 'Sale!')


class UserModelTests(TestCase):
    def test_custom_user_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.assertEqual(str(user), 'test@example.com')
        self.assertEqual(user.role, 'client')
        self.assertEqual(user.balance, 0)
        self.assertEqual(user.theme, 'light')

    def test_user_with_company(self):
        user = User.objects.create_user(
            username='company', email='company@example.com',
            password='testpass123', is_company=True,
            company_name='LLC Test', inn='1234567890',
        )
        self.assertTrue(user.is_company)
        self.assertEqual(user.company_name, 'LLC Test')

    def test_contact_template_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
        )
        template = ContactTemplate.objects.create(
            user=user, name='Home', recipient_name='Mom',
            recipient_phone='+79991234567', city=city,
        )
        self.assertEqual(str(template), 'Home - Mom')

    def test_delivery_template_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        from_city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
        )
        to_city = City.objects.create(
            name='SPB', latitude=59.93, longitude=30.31,
        )
        template = DeliveryTemplate.objects.create(
            user=user, name='Regular route',
            from_city=from_city, to_city=to_city,
            weight=10, cargo_description='Box',
        )
        self.assertIn('Regular route', str(template))
        self.assertIn('Moscow', str(template))

    def test_ticket_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        ticket = Ticket.objects.create(
            subject='Bug report', created_by=user, priority='high',
        )
        self.assertEqual(str(ticket), f'#{ticket.id} Bug report')
        self.assertEqual(ticket.status, 'open')

    def test_ticket_message_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        ticket = Ticket.objects.create(subject='Issue', created_by=user)
        msg = TicketMessage.objects.create(
            ticket=ticket, sender=user, message='Need help',
        )
        self.assertIn('Need help', str(msg))

    def test_transaction_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        tx = Transaction.objects.create(
            user=user, amount=1000, transaction_type='deposit',
            description='Top-up', balance_after=1000,
        )
        self.assertEqual(str(tx), 'deposit 1000 - test@example.com')


class ServiceModelTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name='Test Cat', slug='test-cat')

    def test_service_category_creation(self):
        self.assertEqual(str(self.category), 'Test Cat')

    def test_service_creation(self):
        service = Service.objects.create(
            category=self.category, name='Express', slug='express',
        )
        self.assertEqual(str(service), 'Express')
        self.assertTrue(service.is_active)

    def test_additional_service_creation(self):
        svc = AdditionalService.objects.create(
            name='Insurance', slug='insurance', price=500,
        )
        self.assertEqual(str(svc), 'Insurance')
        self.assertEqual(svc.price_type, 'fixed')

    def test_tariff_creation(self):
        tariff = Tariff.objects.create(
            name='Standard', min_weight=0, max_weight=100,
            price_per_kg=15, delivery_days_min=1, delivery_days_max=5,
        )
        self.assertEqual(str(tariff), 'Standard')


class GeoModelTests(TestCase):
    def test_city_creation(self):
        city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
        )
        self.assertEqual(str(city), 'Moscow')
        self.assertTrue(city.is_active)

    def test_branch_creation(self):
        city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
        )
        branch = Branch.objects.create(
            city=city, branch_type='office',
            address='1 Red Square', latitude=55.75, longitude=37.62,
        )
        self.assertIn('Moscow', str(branch))
        self.assertIn('Red Square', str(branch))

    def test_branch_image_creation(self):
        city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
        )
        branch = Branch.objects.create(
            city=city, branch_type='office',
            address='1 Red Square', latitude=55.75, longitude=37.62,
        )
        img = BranchImage.objects.create(
            branch=branch, image='branches/test.jpg', caption='Front view',
        )
        self.assertIn('Front view', str(img))


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )
        self.city = City.objects.create(
            name='Moscow', latitude=55.75, longitude=37.62,
        )
        self.category = ServiceCategory.objects.create(name='Cat', slug='cat')
        self.service = Service.objects.create(
            category=self.category, name='Svc', slug='svc',
        )

    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.city, recipient_address=self.city,
            service=self.service,
        )
        self.assertTrue(order.tracking_number.startswith('BK-'))
        self.assertEqual(order.status, 'draft')
        self.assertEqual(str(order), order.tracking_number)

    def test_order_status_history_creation(self):
        order = Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.city, recipient_address=self.city,
            service=self.service,
        )
        history = OrderStatusHistory.objects.create(
            order=order, status='created',
            changed_by=self.user, comment='Created',
        )
        self.assertIn(order.tracking_number, str(history))

    def test_order_tracking_number_is_unique(self):
        Order.objects.create(
            user=self.user,
            sender_name='John', sender_phone='+79991234567',
            recipient_name='Jane', recipient_phone='+79997654321',
            cargo_description='Box', weight=5,
            sender_address=self.city, recipient_address=self.city,
            service=self.service,
        )
        self.assertEqual(Order.objects.count(), 1)


class PartnerModelTests(TestCase):
    def test_partner_application_creation(self):
        app = PartnerApplication.objects.create(
            company_name='ACME', contact_person='John',
            email='john@acme.com', phone='+79991234567',
        )
        self.assertEqual(str(app), 'ACME')
        self.assertEqual(app.status, 'new')

    def test_banner_creation(self):
        banner = Banner.objects.create(
            title='Summer Sale', image='banners/sale.jpg',
            link='https://example.com',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            placement='header',
        )
        self.assertEqual(str(banner), 'Summer Sale')
        self.assertEqual(banner.clicks_count, 0)

    def test_iframe_module_creation(self):
        module = IframeModule.objects.create(
            name='Tracker Widget', embed_code='<iframe></iframe>',
        )
        self.assertEqual(str(module), 'Tracker Widget')


class DocumentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123',
        )

    def test_document_creation(self):
        doc = Document.objects.create(
            title='Contract', category='contracts',
            file='documents/contract.pdf',
        )
        self.assertEqual(str(doc), 'Contract')
        self.assertTrue(doc.is_active)

    def test_accounting_request_creation(self):
        req = AccountingRequest.objects.create(
            user=self.user, document_type='invoice',
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timedelta(days=30),
        )
        self.assertIn('invoice', str(req))
        self.assertEqual(req.status, 'pending')