from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import (
    ContentPage,
    FAQ,
    Review,
    NewsItem,
    Vacancy,
    ContactMessage,
    Tender,
    Promotion,
)
from apps.users.models import CustomUser
from apps.services.models import ServiceCategory, Service, AdditionalService, Tariff
from apps.geo.models import City, Branch
from apps.partners.models import PartnerApplication, Banner, IframeModule
from apps.documents.models import Document


class Command(BaseCommand):
    help = 'Seed the database with comprehensive demo data for Baikal-Service'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['force']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_data()

        self.stdout.write(self.style.NOTICE('Seeding data...'))
        self._seed_cities()
        self._seed_branches()
        self._seed_service_categories()
        self._seed_services()
        self._seed_additional_services()
        self._seed_tariffs()
        self._seed_content_pages()
        self._seed_news()
        self._seed_faq()
        self._seed_reviews()
        self._seed_vacancies()
        self._seed_promotions()
        self._seed_tenders()
        self._seed_partner_data()
        self._seed_documents()
        self._seed_superuser()
        self.stdout.write(self.style.SUCCESS('Done seeding data!'))

    def _clear_data(self):
        Document.objects.all().delete()
        IframeModule.objects.all().delete()
        Banner.objects.all().delete()
        PartnerApplication.objects.all().delete()
        Branch.objects.all().delete()
        City.objects.all().delete()
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()
        AdditionalService.objects.all().delete()
        Tariff.objects.all().delete()
        ContentPage.objects.all().delete()
        FAQ.objects.all().delete()
        Review.objects.all().delete()
        NewsItem.objects.all().delete()
        Vacancy.objects.all().delete()
        Tender.objects.all().delete()
        Promotion.objects.all().delete()
        ContactMessage.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        CustomUser.objects.filter(is_superuser=True).delete()

    def _seed_cities(self):
        cities_data = [
            # Russia
            {'name': 'Москва', 'name_en': 'Moscow', 'region': 'Московская область', 'region_en': 'Moscow Oblast', 'lat': 55.7558, 'lng': 37.6176, 'tz': 'Europe/Moscow'},
            {'name': 'Санкт-Петербург', 'name_en': 'Saint Petersburg', 'region': 'Ленинградская область', 'region_en': 'Leningrad Oblast', 'lat': 59.9343, 'lng': 30.3351, 'tz': 'Europe/Moscow'},
            {'name': 'Новосибирск', 'name_en': 'Novosibirsk', 'region': 'Новосибирская область', 'region_en': 'Novosibirsk Oblast', 'lat': 55.0084, 'lng': 82.9357, 'tz': 'Asia/Novosibirsk'},
            {'name': 'Екатеринбург', 'name_en': 'Yekaterinburg', 'region': 'Свердловская область', 'region_en': 'Sverdlovsk Oblast', 'lat': 56.8389, 'lng': 60.6057, 'tz': 'Asia/Yekaterinburg'},
            {'name': 'Казань', 'name_en': 'Kazan', 'region': 'Татарстан', 'region_en': 'Tatarstan', 'lat': 55.7961, 'lng': 49.1064, 'tz': 'Europe/Moscow'},
            {'name': 'Нижний Новгород', 'name_en': 'Nizhny Novgorod', 'region': 'Нижегородская область', 'region_en': 'Nizhny Novgorod Oblast', 'lat': 56.2965, 'lng': 43.9361, 'tz': 'Europe/Moscow'},
            {'name': 'Челябинск', 'name_en': 'Chelyabinsk', 'region': 'Челябинская область', 'region_en': 'Chelyabinsk Oblast', 'lat': 55.1600, 'lng': 61.4028, 'tz': 'Asia/Yekaterinburg'},
            {'name': 'Самара', 'name_en': 'Samara', 'region': 'Самарская область', 'region_en': 'Samara Oblast', 'lat': 53.1959, 'lng': 50.1002, 'tz': 'Europe/Samara'},
            {'name': 'Омск', 'name_en': 'Omsk', 'region': 'Омская область', 'region_en': 'Omsk Oblast', 'lat': 54.9885, 'lng': 73.3242, 'tz': 'Asia/Omsk'},
            {'name': 'Ростов-на-Дону', 'name_en': 'Rostov-on-Don', 'region': 'Ростовская область', 'region_en': 'Rostov Oblast', 'lat': 47.2357, 'lng': 39.7015, 'tz': 'Europe/Moscow'},
            {'name': 'Уфа', 'name_en': 'Ufa', 'region': 'Башкортостан', 'region_en': 'Bashkortostan', 'lat': 54.7388, 'lng': 55.9721, 'tz': 'Asia/Yekaterinburg'},
            {'name': 'Красноярск', 'name_en': 'Krasnoyarsk', 'region': 'Красноярский край', 'region_en': 'Krasnoyarsk Krai', 'lat': 56.0153, 'lng': 92.8932, 'tz': 'Asia/Krasnoyarsk'},
            {'name': 'Воронеж', 'name_en': 'Voronezh', 'region': 'Воронежская область', 'region_en': 'Voronezh Oblast', 'lat': 51.6720, 'lng': 39.1843, 'tz': 'Europe/Moscow'},
            {'name': 'Пермь', 'name_en': 'Perm', 'region': 'Пермский край', 'region_en': 'Perm Krai', 'lat': 58.0105, 'lng': 56.2502, 'tz': 'Asia/Yekaterinburg'},
            {'name': 'Волгоград', 'name_en': 'Volgograd', 'region': 'Волгоградская область', 'region_en': 'Volgograd Oblast', 'lat': 48.7080, 'lng': 44.5133, 'tz': 'Europe/Moscow'},
            {'name': 'Краснодар', 'name_en': 'Krasnodar', 'region': 'Краснодарский край', 'region_en': 'Krasnodar Krai', 'lat': 45.0355, 'lng': 38.9753, 'tz': 'Europe/Moscow'},
            {'name': 'Саратов', 'name_en': 'Saratov', 'region': 'Саратовская область', 'region_en': 'Saratov Oblast', 'lat': 51.5336, 'lng': 46.0343, 'tz': 'Europe/Saratov'},
            {'name': 'Тюмень', 'name_en': 'Tyumen', 'region': 'Тюменская область', 'region_en': 'Tyumen Oblast', 'lat': 57.1530, 'lng': 65.5343, 'tz': 'Asia/Yekaterinburg'},
            {'name': 'Тольятти', 'name_en': 'Tolyatti', 'region': 'Самарская область', 'region_en': 'Samara Oblast', 'lat': 53.5303, 'lng': 49.3461, 'tz': 'Europe/Samara'},
            {'name': 'Барнаул', 'name_en': 'Barnaul', 'region': 'Алтайский край', 'region_en': 'Altai Krai', 'lat': 53.3548, 'lng': 83.7697, 'tz': 'Asia/Barnaul'},
            {'name': 'Ижевск', 'name_en': 'Izhevsk', 'region': 'Удмуртия', 'region_en': 'Udmurtia', 'lat': 56.8498, 'lng': 53.2045, 'tz': 'Europe/Samara'},
            {'name': 'Ульяновск', 'name_en': 'Ulyanovsk', 'region': 'Ульяновская область', 'region_en': 'Ulyanovsk Oblast', 'lat': 54.3142, 'lng': 48.4031, 'tz': 'Europe/Moscow'},
            {'name': 'Иркутск', 'name_en': 'Irkutsk', 'region': 'Иркутская область', 'region_en': 'Irkutsk Oblast', 'lat': 52.2864, 'lng': 104.2807, 'tz': 'Asia/Irkutsk'},
            {'name': 'Хабаровск', 'name_en': 'Khabarovsk', 'region': 'Хабаровский край', 'region_en': 'Khabarovsk Krai', 'lat': 48.4802, 'lng': 135.0719, 'tz': 'Asia/Vladivostok'},
            {'name': 'Владивосток', 'name_en': 'Vladivostok', 'region': 'Приморский край', 'region_en': 'Primorsky Krai', 'lat': 43.1198, 'lng': 131.8869, 'tz': 'Asia/Vladivostok'},
            {'name': 'Калининград', 'name_en': 'Kaliningrad', 'region': 'Калининградская область', 'region_en': 'Kaliningrad Oblast', 'lat': 54.7104, 'lng': 20.4522, 'tz': 'Europe/Kaliningrad'},
            # Belarus
            {'name': 'Минск', 'name_en': 'Minsk', 'region': 'Минская область', 'region_en': 'Minsk Region', 'lat': 53.9045, 'lng': 27.5615, 'tz': 'Europe/Minsk', 'country': 'BY'},
            # Kazakhstan
            {'name': 'Алматы', 'name_en': 'Almaty', 'region': 'Алматинская область', 'region_en': 'Almaty Region', 'lat': 43.2220, 'lng': 76.8512, 'tz': 'Asia/Almaty', 'country': 'KZ'},
            {'name': 'Нур-Султан', 'name_en': 'Nur-Sultan', 'region': 'Акмолинская область', 'region_en': 'Akmola Region', 'lat': 51.1694, 'lng': 71.4491, 'tz': 'Asia/Almaty', 'country': 'KZ'},
            # Kyrgyzstan
            {'name': 'Бишкек', 'name_en': 'Bishkek', 'region': 'Чуйская область', 'region_en': 'Chuy Region', 'lat': 42.8746, 'lng': 74.5698, 'tz': 'Asia/Bishkek', 'country': 'KG'},
            # China
            {'name': 'Пекин', 'name_en': 'Beijing', 'region': 'Пекин', 'region_en': 'Beijing', 'lat': 39.9042, 'lng': 116.4074, 'tz': 'Asia/Shanghai', 'country': 'CN'},
            {'name': 'Шанхай', 'name_en': 'Shanghai', 'region': 'Шанхай', 'region_en': 'Shanghai', 'lat': 31.2304, 'lng': 121.4737, 'tz': 'Asia/Shanghai', 'country': 'CN'},
        ]

        cities = []
        for c in cities_data:
            city = City(
                name=c['name'],
                name_en=c['name_en'],
                region=c['region'],
                region_en=c['region_en'],
                latitude=c['lat'],
                longitude=c['lng'],
                timezone=c['tz'],
                is_active=True,
                country=c.get('country', 'RU'),
            )
            cities.append(city)

        City.objects.bulk_create(cities)
        self.stdout.write(f'  Created {len(cities)} cities')

    def _seed_branches(self):
        city_map = {city.name: city for city in City.objects.all()}

        branches_data = [
            # Moscow (multiple branches)
            {'city': 'Москва', 'type': 'office', 'address': 'ул. Тверская, д. 15', 'phone': '+7 (495) 123-45-67', 'lat': 55.7658, 'lng': 37.6066, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Москва', 'type': 'warehouse', 'address': 'МКАД, 14-й км, вл. 1', 'phone': '+7 (495) 234-56-78', 'lat': 55.6850, 'lng': 37.6450, 'pickup': True, 'delivery': True, 'loading': True},
            {'city': 'Москва', 'type': 'pickup_point', 'address': 'ул. Ленина, д. 42', 'phone': '+7 (495) 345-67-89', 'lat': 55.7450, 'lng': 37.5850, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Москва', 'type': 'warehouse', 'address': 'Шоссе Энтузиастов, д. 100', 'phone': '+7 (495) 456-78-90', 'lat': 55.7550, 'lng': 37.7450, 'pickup': True, 'delivery': True, 'loading': True},
            {'city': 'Москва', 'type': 'office', 'address': 'пр-т Мира, д. 88', 'phone': '+7 (495) 567-89-01', 'lat': 55.7850, 'lng': 37.6350, 'pickup': False, 'delivery': False, 'loading': False},
            # Saint Petersburg
            {'city': 'Санкт-Петербург', 'type': 'office', 'address': 'Невский пр-т, д. 50', 'phone': '+7 (812) 123-45-67', 'lat': 59.9343, 'lng': 30.3150, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Санкт-Петербург', 'type': 'warehouse', 'address': 'ул. Салова, д. 55', 'phone': '+7 (812) 234-56-78', 'lat': 59.8900, 'lng': 30.3700, 'pickup': True, 'delivery': True, 'loading': True},
            {'city': 'Санкт-Петербург', 'type': 'pickup_point', 'address': 'Московский пр-т, д. 122', 'phone': '+7 (812) 345-67-89', 'lat': 59.9050, 'lng': 30.3300, 'pickup': True, 'delivery': False, 'loading': False},
            # Novosibirsk
            {'city': 'Новосибирск', 'type': 'office', 'address': 'ул. Красный пр-т, д. 50', 'phone': '+7 (383) 123-45-67', 'lat': 55.0280, 'lng': 82.9200, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Новосибирск', 'type': 'warehouse', 'address': 'ул. Большевистская, д. 135', 'phone': '+7 (383) 234-56-78', 'lat': 54.9700, 'lng': 82.9500, 'pickup': True, 'delivery': True, 'loading': True},
            # Yekaterinburg
            {'city': 'Екатеринбург', 'type': 'office', 'address': 'пр-т Ленина, д. 24', 'phone': '+7 (343) 123-45-67', 'lat': 56.8380, 'lng': 60.5950, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Екатеринбург', 'type': 'warehouse', 'address': 'ул. Щербакова, д. 4', 'phone': '+7 (343) 234-56-78', 'lat': 56.8100, 'lng': 60.6550, 'pickup': True, 'delivery': True, 'loading': True},
            # Kazan
            {'city': 'Казань', 'type': 'office', 'address': 'ул. Баумана, д. 35', 'phone': '+7 (843) 123-45-67', 'lat': 55.7880, 'lng': 49.1050, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Казань', 'type': 'warehouse', 'address': 'ул. Тэцевская, д. 1', 'phone': '+7 (843) 234-56-78', 'lat': 55.8300, 'lng': 49.0750, 'pickup': True, 'delivery': True, 'loading': True},
            # Nizhny Novgorod
            {'city': 'Нижний Новгород', 'type': 'office', 'address': 'ул. Большая Покровская, д. 60', 'phone': '+7 (831) 123-45-67', 'lat': 56.3260, 'lng': 43.9950, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Нижний Новгород', 'type': 'warehouse', 'address': 'ул. Коминтерна, д. 30', 'phone': '+7 (831) 234-56-78', 'lat': 56.3400, 'lng': 43.8800, 'pickup': True, 'delivery': True, 'loading': True},
            # Chelyabinsk
            {'city': 'Челябинск', 'type': 'office', 'address': 'ул. Кирова, д. 140', 'phone': '+7 (351) 123-45-67', 'lat': 55.1500, 'lng': 61.3950, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Челябинск', 'type': 'warehouse', 'address': 'ул. Северная, д. 25', 'phone': '+7 (351) 234-56-78', 'lat': 55.1900, 'lng': 61.4300, 'pickup': True, 'delivery': True, 'loading': True},
            # Samara
            {'city': 'Самара', 'type': 'office', 'address': 'ул. Молодогвардейская, д. 100', 'phone': '+7 (846) 123-45-67', 'lat': 53.1950, 'lng': 50.0900, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Самара', 'type': 'warehouse', 'address': 'ул. Алма-Атинская, д. 45', 'phone': '+7 (846) 234-56-78', 'lat': 53.2200, 'lng': 50.1300, 'pickup': True, 'delivery': True, 'loading': True},
            # Omsk
            {'city': 'Омск', 'type': 'office', 'address': 'ул. Ленина, д. 22', 'phone': '+7 (3812) 123-45-67', 'lat': 54.9800, 'lng': 73.3700, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Омск', 'type': 'warehouse', 'address': 'пр-т К. Маркса, д. 80', 'phone': '+7 (3812) 234-56-78', 'lat': 55.0100, 'lng': 73.2900, 'pickup': True, 'delivery': True, 'loading': True},
            # Rostov-on-Don
            {'city': 'Ростов-на-Дону', 'type': 'office', 'address': 'ул. Большая Садовая, д. 66', 'phone': '+7 (863) 123-45-67', 'lat': 47.2250, 'lng': 39.7100, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Ростов-на-Дону', 'type': 'warehouse', 'address': 'ул. Вавилова, д. 60', 'phone': '+7 (863) 234-56-78', 'lat': 47.2650, 'lng': 39.6800, 'pickup': True, 'delivery': True, 'loading': True},
            # Ufa
            {'city': 'Уфа', 'type': 'office', 'address': 'пр-т Октября, д. 101', 'phone': '+7 (347) 123-45-67', 'lat': 54.7350, 'lng': 55.9650, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Уфа', 'type': 'warehouse', 'address': 'ул. Трамвайная, д. 12', 'phone': '+7 (347) 234-56-78', 'lat': 54.7700, 'lng': 56.0000, 'pickup': True, 'delivery': True, 'loading': True},
            # Krasnoyarsk
            {'city': 'Красноярск', 'type': 'office', 'address': 'пр-т Мира, д. 55', 'phone': '+7 (391) 123-45-67', 'lat': 56.0150, 'lng': 92.8800, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Красноярск', 'type': 'warehouse', 'address': 'ул. Калинина, д. 40', 'phone': '+7 (391) 234-56-78', 'lat': 55.9800, 'lng': 92.9200, 'pickup': True, 'delivery': True, 'loading': True},
            # Voronezh
            {'city': 'Воронеж', 'type': 'office', 'address': 'ул. Пушкинская, д. 12', 'phone': '+7 (473) 123-45-67', 'lat': 51.6650, 'lng': 39.1950, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Воронеж', 'type': 'warehouse', 'address': 'ул. 9 Января, д. 168', 'phone': '+7 (473) 234-56-78', 'lat': 51.7000, 'lng': 39.1550, 'pickup': True, 'delivery': True, 'loading': True},
            # Perm
            {'city': 'Пермь', 'type': 'office', 'address': 'ул. Ленина, д. 75', 'phone': '+7 (342) 123-45-67', 'lat': 58.0050, 'lng': 56.2350, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Пермь', 'type': 'warehouse', 'address': 'ул. Промышленная, д. 15', 'phone': '+7 (342) 234-56-78', 'lat': 58.0400, 'lng': 56.2800, 'pickup': True, 'delivery': True, 'loading': True},
            # Volgograd
            {'city': 'Волгоград', 'type': 'office', 'address': 'пр-т Ленина, д. 96', 'phone': '+7 (8442) 123-45-67', 'lat': 48.7100, 'lng': 44.5200, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Волгоград', 'type': 'warehouse', 'address': 'ул. Невская, д. 50', 'phone': '+7 (8442) 234-56-78', 'lat': 48.6800, 'lng': 44.4850, 'pickup': True, 'delivery': True, 'loading': True},
            # Krasnodar
            {'city': 'Краснодар', 'type': 'office', 'address': 'ул. Красная, д. 100', 'phone': '+7 (861) 123-45-67', 'lat': 45.0350, 'lng': 38.9700, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Краснодар', 'type': 'warehouse', 'address': 'ул. Уральская, д. 88', 'phone': '+7 (861) 234-56-78', 'lat': 45.0600, 'lng': 38.9950, 'pickup': True, 'delivery': True, 'loading': True},
            # Saratov
            {'city': 'Саратов', 'type': 'office', 'address': 'ул. Московская, д. 85', 'phone': '+7 (8452) 123-45-67', 'lat': 51.5300, 'lng': 46.0400, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Саратов', 'type': 'warehouse', 'address': 'ул. Чернышевского, д. 200', 'phone': '+7 (8452) 234-56-78', 'lat': 51.5550, 'lng': 46.0050, 'pickup': True, 'delivery': True, 'loading': True},
            # Tyumen
            {'city': 'Тюмень', 'type': 'office', 'address': 'ул. Республики, д. 60', 'phone': '+7 (3452) 123-45-67', 'lat': 57.1550, 'lng': 65.5400, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Тюмень', 'type': 'warehouse', 'address': 'ул. Московский тракт, д. 130', 'phone': '+7 (3452) 234-56-78', 'lat': 57.1280, 'lng': 65.4900, 'pickup': True, 'delivery': True, 'loading': True},
            # Tolyatti
            {'city': 'Тольятти', 'type': 'office', 'address': 'ул. Мира, д. 42', 'phone': '+7 (8482) 123-45-67', 'lat': 53.5300, 'lng': 49.3500, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Тольятти', 'type': 'pickup_point', 'address': 'ул. Ленина, д. 60', 'phone': '+7 (8482) 234-56-78', 'lat': 53.5150, 'lng': 49.3300, 'pickup': True, 'delivery': False, 'loading': False},
            # Barnaul
            {'city': 'Барнаул', 'type': 'office', 'address': 'пр-т Ленина, д. 30', 'phone': '+7 (3852) 123-45-67', 'lat': 53.3550, 'lng': 83.7700, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Барнаул', 'type': 'warehouse', 'address': 'ул. Попова, д. 75', 'phone': '+7 (3852) 234-56-78', 'lat': 53.3750, 'lng': 83.7900, 'pickup': True, 'delivery': True, 'loading': True},
            # Izhevsk
            {'city': 'Ижевск', 'type': 'office', 'address': 'ул. Пушкинская, д. 175', 'phone': '+7 (3412) 123-45-67', 'lat': 56.8500, 'lng': 53.2000, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Ижевск', 'type': 'warehouse', 'address': 'ул. Новоажимова, д. 1', 'phone': '+7 (3412) 234-56-78', 'lat': 56.8700, 'lng': 53.2300, 'pickup': True, 'delivery': True, 'loading': True},
            # Ulyanovsk
            {'city': 'Ульяновск', 'type': 'office', 'address': 'ул. Гончарова, д. 30', 'phone': '+7 (8422) 123-45-67', 'lat': 54.3150, 'lng': 48.4000, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Ульяновск', 'type': 'warehouse', 'address': 'ул. Московское шоссе, д. 55', 'phone': '+7 (8422) 234-56-78', 'lat': 54.2850, 'lng': 48.3750, 'pickup': True, 'delivery': True, 'loading': True},
            # Irkutsk
            {'city': 'Иркутск', 'type': 'office', 'address': 'ул. Карла Маркса, д. 40', 'phone': '+7 (3952) 123-45-67', 'lat': 52.2850, 'lng': 104.2800, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Иркутск', 'type': 'warehouse', 'address': 'ул. Трактовая, д. 22', 'phone': '+7 (3952) 234-56-78', 'lat': 52.3100, 'lng': 104.3100, 'pickup': True, 'delivery': True, 'loading': True},
            # Khabarovsk
            {'city': 'Хабаровск', 'type': 'office', 'address': 'ул. Муравьёва-Амурского, д. 50', 'phone': '+7 (4212) 123-45-67', 'lat': 48.4800, 'lng': 135.0700, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Хабаровск', 'type': 'warehouse', 'address': 'ул. Промышленная, д. 10', 'phone': '+7 (4212) 234-56-78', 'lat': 48.5050, 'lng': 135.1000, 'pickup': True, 'delivery': True, 'loading': True},
            # Vladivostok
            {'city': 'Владивосток', 'type': 'office', 'address': 'ул. Светланская, д. 80', 'phone': '+7 (423) 123-45-67', 'lat': 43.1150, 'lng': 131.8850, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Владивосток', 'type': 'warehouse', 'address': 'ул. Русская, д. 65', 'phone': '+7 (423) 234-56-78', 'lat': 43.1450, 'lng': 131.9100, 'pickup': True, 'delivery': True, 'loading': True},
            # Kaliningrad
            {'city': 'Калининград', 'type': 'office', 'address': 'ул. Мира, д. 18', 'phone': '+7 (4012) 123-45-67', 'lat': 54.7100, 'lng': 20.4550, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Калининград', 'type': 'warehouse', 'address': 'ул. Дзержинского, д. 55', 'phone': '+7 (4012) 234-56-78', 'lat': 54.6900, 'lng': 20.4300, 'pickup': True, 'delivery': True, 'loading': True},
            # Minsk
            {'city': 'Минск', 'type': 'office', 'address': 'пр-т Независимости, д. 100', 'phone': '+375 (17) 123-45-67', 'lat': 53.9000, 'lng': 27.5700, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Минск', 'type': 'warehouse', 'address': 'ул. Тимирязева, д. 75', 'phone': '+375 (17) 234-56-78', 'lat': 53.9300, 'lng': 27.5300, 'pickup': True, 'delivery': True, 'loading': True},
            {'city': 'Минск', 'type': 'pickup_point', 'address': 'ул. Немига, д. 12', 'phone': '+375 (17) 345-67-89', 'lat': 53.9050, 'lng': 27.5500, 'pickup': True, 'delivery': False, 'loading': False},
            # Almaty
            {'city': 'Алматы', 'type': 'office', 'address': 'пр-т Абая, д. 150', 'phone': '+7 (727) 123-45-67', 'lat': 43.2200, 'lng': 76.8550, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Алматы', 'type': 'warehouse', 'address': 'ул. Майлина, д. 30', 'phone': '+7 (727) 234-56-78', 'lat': 43.2450, 'lng': 76.8800, 'pickup': True, 'delivery': True, 'loading': True},
            # Nur-Sultan
            {'city': 'Нур-Султан', 'type': 'office', 'address': 'пр-т Кабанбай батыра, д. 20', 'phone': '+7 (7172) 123-45-67', 'lat': 51.1650, 'lng': 71.4450, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Нур-Султан', 'type': 'warehouse', 'address': 'ул. Сарайшык, д. 15', 'phone': '+7 (7172) 234-56-78', 'lat': 51.1900, 'lng': 71.4700, 'pickup': True, 'delivery': True, 'loading': True},
            # Bishkek
            {'city': 'Бишкек', 'type': 'office', 'address': 'пр-т Чуй, д. 200', 'phone': '+996 (312) 123-45-67', 'lat': 42.8750, 'lng': 74.5700, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Бишкек', 'type': 'warehouse', 'address': 'ул. Льва Толстого, д. 80', 'phone': '+996 (312) 234-56-78', 'lat': 42.8500, 'lng': 74.5950, 'pickup': True, 'delivery': True, 'loading': True},
            # Beijing
            {'city': 'Пекин', 'type': 'office', 'address': 'Chaoyang District, Jianguomen Outer St, 18', 'phone': '+86 (10) 1234-5678', 'lat': 39.9050, 'lng': 116.4100, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Пекин', 'type': 'warehouse', 'address': 'Tongzhou District, Zhangjiawan Industrial Park', 'phone': '+86 (10) 2345-6789', 'lat': 39.8600, 'lng': 116.6600, 'pickup': True, 'delivery': True, 'loading': True},
            # Shanghai
            {'city': 'Шанхай', 'type': 'office', 'address': 'Pudong, Lujiazui Financial Center, 1200', 'phone': '+86 (21) 1234-5678', 'lat': 31.2350, 'lng': 121.5000, 'pickup': True, 'delivery': True, 'loading': False},
            {'city': 'Шанхай', 'type': 'warehouse', 'address': 'Minhang District, Hongmei Road, 2800', 'phone': '+86 (21) 2345-6789', 'lat': 31.1800, 'lng': 121.4000, 'pickup': True, 'delivery': True, 'loading': True},
            # Additional branches to reach 80+
            {'city': 'Москва', 'type': 'pickup_point', 'address': 'ул. Арбат, д. 30', 'phone': '+7 (495) 678-90-12', 'lat': 55.7480, 'lng': 37.5900, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Санкт-Петербург', 'type': 'pickup_point', 'address': 'ул. Садовая, д. 40', 'phone': '+7 (812) 456-78-90', 'lat': 59.9250, 'lng': 30.3150, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Новосибирск', 'type': 'pickup_point', 'address': 'ул. Советская, д. 30', 'phone': '+7 (383) 345-67-89', 'lat': 55.0350, 'lng': 82.9300, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Екатеринбург', 'type': 'pickup_point', 'address': 'ул. Малышева, д. 55', 'phone': '+7 (343) 345-67-89', 'lat': 56.8400, 'lng': 60.6100, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Казань', 'type': 'pickup_point', 'address': 'ул. Кремлёвская, д. 25', 'phone': '+7 (843) 345-67-89', 'lat': 55.7930, 'lng': 49.1100, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Нижний Новгород', 'type': 'pickup_point', 'address': 'ул. Рождественская, д. 20', 'phone': '+7 (831) 345-67-89', 'lat': 56.3300, 'lng': 43.9700, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Самара', 'type': 'pickup_point', 'address': 'ул. Куйбышева, д. 70', 'phone': '+7 (846) 345-67-89', 'lat': 53.1880, 'lng': 50.0850, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Ростов-на-Дону', 'type': 'pickup_point', 'address': 'ул. Пушкинская, д. 150', 'phone': '+7 (863) 345-67-89', 'lat': 47.2300, 'lng': 39.7050, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Краснодар', 'type': 'pickup_point', 'address': 'ул. Северная, д. 350', 'phone': '+7 (861) 345-67-89', 'lat': 45.0420, 'lng': 38.9800, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Волгоград', 'type': 'pickup_point', 'address': 'ул. Советская, д. 30', 'phone': '+7 (8442) 345-67-89', 'lat': 48.7200, 'lng': 44.5150, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Владивосток', 'type': 'pickup_point', 'address': 'ул. Алеутская, д. 15', 'phone': '+7 (423) 345-67-89', 'lat': 43.1220, 'lng': 131.8900, 'pickup': True, 'delivery': False, 'loading': False},
            {'city': 'Калининград', 'type': 'pickup_point', 'address': 'ул. Ленинский пр-т, д. 40', 'phone': '+7 (4012) 345-67-89', 'lat': 54.7050, 'lng': 20.5000, 'pickup': True, 'delivery': False, 'loading': False},
        ]

        working_hours_default = {
            'mon-fri': '09:00-18:00',
            'sat': '10:00-16:00',
            'sun': 'closed',
        }
        warehouse_hours = {
            'mon-fri': '08:00-20:00',
            'sat': '09:00-17:00',
            'sun': '10:00-14:00',
        }
        pickup_hours = {
            'mon-fri': '09:00-21:00',
            'sat': '10:00-18:00',
            'sun': '11:00-16:00',
        }

        branches = []
        email_map = {
            'office': 'office',
            'warehouse': 'warehouse',
            'pickup_point': 'pickup',
        }
        for b in branches_data:
            hours = working_hours_default
            if b['type'] == 'warehouse':
                hours = warehouse_hours
            elif b['type'] == 'pickup_point':
                hours = pickup_hours
            branch = Branch(
                city=city_map[b['city']],
                branch_type=b['type'],
                address=b['address'],
                address_en=b['address'],
                phone=b['phone'],
                email=f'{email_map[b["type"]]}@{slugify(b["city"])}.baikal-service.ru',
                working_hours=hours,
                latitude=b['lat'],
                longitude=b['lng'],
                is_active=True,
                has_pickup=b['pickup'],
                has_delivery=b['delivery'],
                has_loading_equipment=b['loading'],
            )
            branches.append(branch)

        Branch.objects.bulk_create(branches)
        self.stdout.write(f'  Created {len(branches)} branches')

    def _seed_service_categories(self):
        categories = [
            {'name': 'Автоперевозки', 'name_en': 'Road Transportation', 'slug': 'cargo-transportation', 'icon': 'fa-truck', 'description': 'Автомобильные грузоперевозки по всей России, СНГ и Китаю', 'description_en': 'Road freight transportation across Russia, CIS, and China', 'order': 1},
            {'name': 'Сборный груз', 'name_en': 'Consolidated Cargo', 'slug': 'consolidated-cargo', 'icon': 'fa-boxes', 'description': 'Консолидированные грузоперевозки по выгодным тарифам', 'description_en': 'Consolidated shipping at competitive rates', 'order': 2},
            {'name': 'Доставка в розничные сети', 'name_en': 'Retail Chain Delivery', 'slug': 'retail-chains', 'icon': 'fa-store', 'description': 'Доставка товаров в крупнейшие розничные сети', 'description_en': 'Delivery to major retail chains', 'order': 3},
            {'name': 'Доставка на маркетплейсы', 'name_en': 'Marketplace Delivery', 'slug': 'marketplaces', 'icon': 'fa-shopping-cart', 'description': 'Доставка на Wildberries, Ozon, Яндекс Маркет и другие', 'description_en': 'Delivery to Wildberries, Ozon, Yandex Market and more', 'order': 4},
            {'name': 'Доставка на стройрынки', 'name_en': 'Construction Market Delivery', 'slug': 'construction-markets', 'icon': 'fa-hard-hat', 'description': 'Доставка на строительные рынки и гипермаркеты', 'description_en': 'Delivery to construction stores and hypermarkets', 'order': 5},
            {'name': 'Тариф «Посылка»', 'name_en': 'Parcel Tariff', 'slug': 'posylka-tariff', 'icon': 'fa-box', 'description': 'Экономичная доставка небольших посылок', 'description_en': 'Affordable small parcel shipping', 'order': 6},
            {'name': 'Паллетные перевозки', 'name_en': 'Pallet Transportation', 'slug': 'pallet-transportation', 'icon': 'fa-pallet', 'description': 'Перевозка грузов на паллетах', 'description_en': 'Palletized cargo shipping', 'order': 7},
            {'name': 'Авиаперевозки', 'name_en': 'Air Cargo', 'slug': 'air-cargo', 'icon': 'fa-plane', 'description': 'Быстрая доставка грузов авиатранспортом', 'description_en': 'Express air freight delivery', 'order': 8},
            {'name': 'Контейнерные перевозки', 'name_en': 'Container Shipping', 'slug': 'container', 'icon': 'fa-ship', 'description': 'Контейнерные перевозки 20ft, 40ft по всем направлениям', 'description_en': '20ft and 40ft container transportation', 'order': 9},
            {'name': 'FТL (Отдельная машина)', 'name_en': 'FTL (Full Truck Load)', 'slug': 'ftl', 'icon': 'fa-truck-moving', 'description': 'Выделенный транспорт для вашего груза', 'description_en': 'Dedicated transport for your cargo', 'order': 10},
            {'name': 'Доставка документов', 'name_en': 'Document Delivery', 'slug': 'document-delivery', 'icon': 'fa-envelope', 'description': 'Экспресс-доставка документов по России', 'description_en': 'Express document delivery across Russia', 'order': 11},
            {'name': 'Виды транспорта', 'name_en': 'Transport Types', 'slug': 'transport-types', 'icon': 'fa-route', 'description': 'Все виды транспорта: авто, ЖД, авиа, море, мультимодальные', 'description_en': 'All transport types: road, rail, air, sea, multimodal', 'order': 12},
        ]
        objs = [ServiceCategory(**c) for c in categories]
        ServiceCategory.objects.bulk_create(objs)
        self.stdout.write(f'  Created {len(objs)} service categories')

    def _seed_services(self):
        cat_map = {cat.slug: cat for cat in ServiceCategory.objects.all()}

        services_data = [
            # Cargo Transportation
            {'cat': 'cargo-transportation', 'name': 'Междугородние перевозки', 'name_en': 'Intercity Shipping', 'slug': 'intercity', 'desc': 'Грузоперевозки между городами России', 'short': 'от 25 ₽/кг', 'icon': 'fa-truck', 'price': Decimal('25.00'), 'unit': '₽/кг', 'order': 1},
            {'cat': 'cargo-transportation', 'name': 'Международные перевозки', 'name_en': 'International Shipping', 'slug': 'international', 'desc': 'Грузоперевозки в СНГ и Китай', 'short': 'от 45 ₽/кг', 'icon': 'fa-globe', 'price': Decimal('45.00'), 'unit': '₽/кг', 'order': 2},
            {'cat': 'cargo-transportation', 'name': 'Перевозка негабаритных грузов', 'name_en': 'Oversized Cargo', 'slug': 'oversized', 'desc': 'Транспортировка крупногабаритных грузов', 'short': 'индивидуальный расчет', 'icon': 'fa-expand', 'price': None, 'unit': '', 'order': 3},
            # Consolidated Cargo
            {'cat': 'consolidated-cargo', 'name': 'Сборные грузы по России', 'name_en': 'Consolidated Cargo Russia', 'slug': 'consolidated-russia', 'desc': 'Консолидация грузов от разных отправителей', 'short': 'от 18 ₽/кг', 'icon': 'fa-boxes', 'price': Decimal('18.00'), 'unit': '₽/кг', 'order': 1},
            {'cat': 'consolidated-cargo', 'name': 'Сборные грузы из Китая', 'name_en': 'Consolidated Cargo from China', 'slug': 'consolidated-china', 'desc': 'Консолидированные поставки из Китая', 'short': 'от 35 ₽/кг', 'icon': 'fa-shipping-fast', 'price': Decimal('35.00'), 'unit': '₽/кг', 'order': 2},
            # Retail Chains
            {'cat': 'retail-chains', 'name': 'Доставка в Пятёрочку', 'name_en': 'Delivery to Pyaterochka', 'slug': 'pyaterochka', 'desc': 'Доставка в сеть магазинов Пятёрочка', 'short': 'индивидуальный тариф', 'icon': 'fa-store', 'price': None, 'unit': '', 'order': 1},
            {'cat': 'retail-chains', 'name': 'Доставка в Магнит', 'name_en': 'Delivery to Magnit', 'slug': 'magnit', 'desc': 'Доставка в сеть магазинов Магнит', 'short': 'индивидуальный тариф', 'icon': 'fa-store-alt', 'price': None, 'unit': '', 'order': 2},
            {'cat': 'retail-chains', 'name': 'Доставка в Ленту', 'name_en': 'Delivery to Lenta', 'slug': 'lenta', 'desc': 'Доставка в гипермаркеты Лента', 'short': 'индивидуальный тариф', 'icon': 'fa-warehouse', 'price': None, 'unit': '', 'order': 3},
            # Marketplaces
            {'cat': 'marketplaces', 'name': 'Доставка на Wildberries', 'name_en': 'Delivery to Wildberries', 'slug': 'wb', 'desc': 'Полный цикл доставки на склад Wildberries', 'short': 'от 22 ₽/кг', 'icon': 'fa-shopping-bag', 'price': Decimal('22.00'), 'unit': '₽/кг', 'order': 1},
            {'cat': 'marketplaces', 'name': 'Доставка на Ozon', 'name_en': 'Delivery to Ozon', 'slug': 'ozon', 'desc': 'Доставка на склады Ozon', 'short': 'от 22 ₽/кг', 'icon': 'fa-shopping-bag', 'price': Decimal('22.00'), 'unit': '₽/кг', 'order': 2},
            {'cat': 'marketplaces', 'name': 'Доставка на Яндекс Маркет', 'name_en': 'Delivery to Yandex Market', 'slug': 'yandex-market', 'desc': 'Доставка на склады Яндекс Маркета', 'short': 'от 20 ₽/кг', 'icon': 'fa-shopping-bag', 'price': Decimal('20.00'), 'unit': '₽/кг', 'order': 3},
            # Construction Markets
            {'cat': 'construction-markets', 'name': 'Доставка в Leroy Merlin', 'name_en': 'Delivery to Leroy Merlin', 'slug': 'leroy-merlin', 'desc': 'Доставка товаров в гипермаркеты Леруа Мерлен', 'short': 'индивидуальный расчет', 'icon': 'fa-hard-hat', 'price': None, 'unit': '', 'order': 1},
            {'cat': 'construction-markets', 'name': 'Доставка стройматериалов', 'name_en': 'Construction Materials Delivery', 'slug': 'construction-materials', 'desc': 'Перевозка строительных материалов и оборудования', 'short': 'от 30 ₽/кг', 'icon': 'fa-tools', 'price': Decimal('30.00'), 'unit': '₽/кг', 'order': 2},
            # Posylka Tariff
            {'cat': 'posylka-tariff', 'name': 'Посылка до 5 кг', 'name_en': 'Parcel up to 5 kg', 'slug': 'parcel-5kg', 'desc': 'Экономичная доставка посылок до 5 кг', 'short': 'от 350 ₽', 'icon': 'fa-box', 'price': Decimal('350.00'), 'unit': '₽', 'order': 1},
            {'cat': 'posylka-tariff', 'name': 'Посылка до 10 кг', 'name_en': 'Parcel up to 10 kg', 'slug': 'parcel-10kg', 'desc': 'Экономичная доставка посылок до 10 кг', 'short': 'от 550 ₽', 'icon': 'fa-box-open', 'price': Decimal('550.00'), 'unit': '₽', 'order': 2},
            {'cat': 'posylka-tariff', 'name': 'Посылка до 20 кг', 'name_en': 'Parcel up to 20 kg', 'slug': 'parcel-20kg', 'desc': 'Экономичная доставка посылок до 20 кг', 'short': 'от 850 ₽', 'icon': 'fa-boxes', 'price': Decimal('850.00'), 'unit': '₽', 'order': 3},
            # Pallet Transportation
            {'cat': 'pallet-transportation', 'name': 'Паллетный борт', 'name_en': 'Pallet Flatbed', 'slug': 'pallet-flatbed', 'desc': 'Перевозка грузов на паллетах', 'short': 'от 200 ₽/паллета', 'icon': 'fa-pallet', 'price': Decimal('200.00'), 'unit': '₽/паллета', 'order': 1},
            # Air Cargo
            {'cat': 'air-cargo', 'name': 'Авиадоставка по России', 'name_en': 'Air Delivery Russia', 'slug': 'air-russia', 'desc': 'Срочная авиадоставка по России', 'short': 'от 150 ₽/кг', 'icon': 'fa-plane', 'price': Decimal('150.00'), 'unit': '₽/кг', 'order': 1},
            {'cat': 'air-cargo', 'name': 'Авиадоставка международная', 'name_en': 'International Air Delivery', 'slug': 'air-international', 'desc': 'Международная авиадоставка', 'short': 'от 350 ₽/кг', 'icon': 'fa-plane-departure', 'price': Decimal('350.00'), 'unit': '₽/кг', 'order': 2},
            # Container
            {'cat': 'container', 'name': '20ft контейнер', 'name_en': '20ft Container', 'slug': 'container-20ft', 'desc': 'Перевозка в 20-футовых контейнерах', 'short': 'от 150 000 ₽', 'icon': 'fa-ship', 'price': Decimal('150000.00'), 'unit': '₽', 'order': 1},
            {'cat': 'container', 'name': '40ft контейнер', 'name_en': '40ft Container', 'slug': 'container-40ft', 'desc': 'Перевозка в 40-футовых контейнерах', 'short': 'от 250 000 ₽', 'icon': 'fa-ship', 'price': Decimal('250000.00'), 'unit': '₽', 'order': 2},
            # FTL
            {'cat': 'ftl', 'name': 'Фургон 20т', 'name_en': 'Truck 20t', 'slug': 'ftl-20t', 'desc': 'Выделенная фура 20 тонн', 'short': 'от 80 000 ₽', 'icon': 'fa-truck-moving', 'price': Decimal('80000.00'), 'unit': '₽', 'order': 1},
            {'cat': 'ftl', 'name': 'Фургон 10т', 'name_en': 'Truck 10t', 'slug': 'ftl-10t', 'desc': 'Выделенная фура 10 тонн', 'short': 'от 50 000 ₽', 'icon': 'fa-truck-moving', 'price': Decimal('50000.00'), 'unit': '₽', 'order': 2},
            {'cat': 'ftl', 'name': 'Рефрижератор', 'name_en': 'Refrigerated Truck', 'slug': 'ftl-refrigerator', 'desc': 'Рефрижератор с температурным режимом', 'short': 'от 100 000 ₽', 'icon': 'fa-snowflake', 'price': Decimal('100000.00'), 'unit': '₽', 'order': 3},
            # Document Delivery
            {'cat': 'document-delivery', 'name': 'Экспресс-доставка документов', 'name_en': 'Express Document Delivery', 'slug': 'express-docs', 'desc': 'Срочная доставка документов по городу и между городами', 'short': 'от 500 ₽', 'icon': 'fa-envelope', 'price': Decimal('500.00'), 'unit': '₽', 'order': 1},
            # Transport Types
            {'cat': 'transport-types', 'name': 'Автомобильные перевозки', 'name_en': 'Road Transport', 'slug': 'road-transport', 'desc': 'Перевозки автотранспортом', 'short': 'от 25 ₽/кг', 'icon': 'fa-truck', 'price': None, 'unit': '', 'order': 1},
            {'cat': 'transport-types', 'name': 'Железнодорожные перевозки', 'name_en': 'Rail Transport', 'slug': 'rail-transport', 'desc': 'Перевозки по железной дороге', 'short': 'от 10 ₽/кг', 'icon': 'fa-train', 'price': Decimal('10.00'), 'unit': '₽/кг', 'order': 2},
            {'cat': 'transport-types', 'name': 'Мультимодальные перевозки', 'name_en': 'Multimodal Transport', 'slug': 'multimodal', 'desc': 'Комбинированные перевозки разными видами транспорта', 'short': 'от 30 ₽/кг', 'icon': 'fa-route', 'price': Decimal('30.00'), 'unit': '₽/кг', 'order': 3},
        ]

        services = []
        for s in services_data:
            services.append(Service(
                category=cat_map[s['cat']],
                name=s['name'],
                name_en=s.get('name_en', ''),
                slug=s['slug'],
                description=s['desc'],
                short_description=s['short'],
                icon=s['icon'],
                base_price=s['price'],
                price_unit=s['unit'],
                is_active=True,
                sort_order=s['order'],
            ))
        Service.objects.bulk_create(services)
        self.stdout.write(f'  Created {len(services)} services')

    def _seed_additional_services(self):
        addons = [
            {'name': 'Забор груза от отправителя', 'name_en': 'Pickup from Sender', 'slug': 'pickup', 'description': 'Забор груза от двери отправителя', 'description_en': 'Cargo pickup from sender door', 'price': Decimal('500.00'), 'price_type': 'fixed'},
            {'name': 'Доставка до получателя', 'name_en': 'Door Delivery', 'slug': 'door-delivery', 'description': 'Доставка груза до двери получателя', 'description_en': 'Cargo delivery to recipient door', 'price': Decimal('800.00'), 'price_type': 'fixed'},
            {'name': 'Доставка до пункта выдачи', 'name_en': 'Pickup Point Delivery', 'slug': 'pickup-point', 'description': 'Доставка до ближайшего пункта выдачи', 'description_en': 'Delivery to nearest pickup point', 'price': Decimal('300.00'), 'price_type': 'fixed'},
            {'name': 'Погрузо-разгрузочные работы', 'name_en': 'Loading & Unloading', 'slug': 'loading-unloading', 'description': 'Погрузка и разгрузка груза', 'description_en': 'Cargo loading and unloading', 'price': Decimal('1500.00'), 'price_type': 'fixed'},
            {'name': 'Страхование груза', 'name_en': 'Cargo Insurance', 'slug': 'insurance', 'description': 'Страхование груза от повреждений и утери', 'description_en': 'Insurance against damage and loss', 'price': Decimal('3.00'), 'price_type': 'percentage'},
            {'name': 'Перевозка сопроводительных документов', 'name_en': 'Shipping Documents', 'slug': 'shipping-docs', 'description': 'Перевозка сопроводительных документов', 'description_en': 'Transportation of accompanying documents', 'price': Decimal('400.00'), 'price_type': 'fixed'},
            {'name': 'Доставка к определенному времени', 'name_en': 'Time-Definite Delivery', 'slug': 'time-definite', 'description': 'Гарантированная доставка к указанному времени', 'description_en': 'Guaranteed delivery by specified time', 'price': Decimal('2000.00'), 'price_type': 'fixed'},
            {'name': 'Подтверждение доставки', 'name_en': 'Delivery Confirmation', 'slug': 'delivery-confirmation', 'description': 'Подтверждение доставки (фото, подпись)', 'description_en': 'Delivery confirmation (photo, signature)', 'price': Decimal('200.00'), 'price_type': 'fixed'},
            {'name': 'SMS-код при получении', 'name_en': 'SMS Code Delivery', 'slug': 'sms-code', 'description': 'Получатель вводит SMS-код для получения груза', 'description_en': 'Recipient enters SMS code to receive cargo', 'price': Decimal('100.00'), 'price_type': 'fixed'},
            {'name': 'Экспресс-обработка', 'name_en': 'Express Processing', 'slug': 'express-delivery', 'description': 'Приоритетная обработка на складе', 'description_en': 'Priority warehouse processing', 'price': Decimal('1200.00'), 'price_type': 'fixed'},
            {'name': 'Технология «Имплант»', 'name_en': 'Implant Technology', 'slug': 'implant-technology', 'description': 'Проприетарная технология бесшовной логистической интеграции', 'description_en': 'Proprietary seamless logistics integration technology', 'price': Decimal('5000.00'), 'price_type': 'fixed'},
        ]
        objs = [AdditionalService(**a) for a in addons]
        AdditionalService.objects.bulk_create(objs)
        self.stdout.write(f'  Created {len(objs)} additional services')

    def _seed_tariffs(self):
        tariffs = [
            {'name': 'Эконом', 'name_en': 'Economy', 'description': 'Базовый тариф для небольших грузов до 10 кг', 'description_en': 'Basic tariff for small cargo up to 10 kg', 'min_weight': 0, 'max_weight': 10, 'price_per_kg': Decimal('35.00'), 'delivery_days_min': 3, 'delivery_days_max': 7},
            {'name': 'Стандарт', 'name_en': 'Standard', 'description': 'Оптимальный тариф для грузов до 50 кг', 'description_en': 'Optimal tariff for cargo up to 50 kg', 'min_weight': 10, 'max_weight': 50, 'price_per_kg': Decimal('28.00'), 'delivery_days_min': 2, 'delivery_days_max': 5},
            {'name': 'Бизнес', 'name_en': 'Business', 'description': 'Тариф для коммерческих грузов до 200 кг', 'description_en': 'Tariff for commercial cargo up to 200 kg', 'min_weight': 50, 'max_weight': 200, 'price_per_kg': Decimal('22.00'), 'delivery_days_min': 2, 'delivery_days_max': 4},
            {'name': 'Оптовый', 'name_en': 'Wholesale', 'description': 'Специальный тариф для крупных партий грузов до 1000 кг', 'description_en': 'Special tariff for bulk shipments up to 1000 kg', 'min_weight': 200, 'max_weight': 1000, 'price_per_kg': Decimal('18.00'), 'delivery_days_min': 1, 'delivery_days_max': 3},
            {'name': 'Корпоративный', 'name_en': 'Corporate', 'description': 'Индивидуальный тариф для корпоративных клиентов от 1000 кг', 'description_en': 'Custom tariff for corporate clients from 1000 kg', 'min_weight': 1000, 'max_weight': None, 'price_per_kg': Decimal('12.00'), 'delivery_days_min': 1, 'delivery_days_max': 3},
            {'name': 'Экспресс', 'name_en': 'Express', 'description': 'Срочная доставка грузов до 30 кг', 'description_en': 'Express delivery for cargo up to 30 kg', 'min_weight': 0, 'max_weight': 30, 'price_per_kg': Decimal('55.00'), 'delivery_days_min': 1, 'delivery_days_max': 2},
        ]
        objs = [Tariff(**t) for t in tariffs]
        Tariff.objects.bulk_create(objs)
        self.stdout.write(f'  Created {len(objs)} tariffs')

    def _seed_content_pages(self):
        pages = [
            {
                'slug': 'about',
                'title': 'О компании',
                'content': '<h2>Байкал-Сервис — лидер логистики в России и СНГ</h2><p>Байкал-Сервис — одна из крупнейших транспортно-логистических компаний России, предоставляющая полный спектр услуг по перевозке грузов. Мы работаем с 1995 года и за это время заслужили доверие более 50 000 клиентов.</p><p>Наша миссия — делать логистику простой, надежной и доступной для каждого. Мы постоянно развиваемся, внедряем новые технологии и расширяем географию присутствия.</p><p>Сегодня Байкал-Сервис — это более 80 филиалов по всей России, в странах СНГ и Китае. Мы доставляем грузы любой сложности: от маленьких посылок до крупногабаритного оборудования.</p>',
                'meta': 'Узнайте о компании Байкал-Сервис — лидере транспортно-логистической отрасли',
                'type': 'about',
                'published': True,
            },
        ]
        for p in pages:
            ContentPage.objects.create(
                slug=p['slug'],
                title=p['title'],
                title_en=p['title'],
                content=p['content'],
                content_en=p['content'],
                meta_description=p['meta'],
                is_published=p['published'],
                page_type=p['type'],
            )
        self.stdout.write(f'  Created {len(pages)} content pages')

    def _seed_news(self):
        now = timezone.now()
        news_items = [
            {
                'title': 'Байкал-Сервис открыл новый терминал в Москве',
                'slug': 'new-terminal-moscow',
                'short': 'Новый складской терминал площадью 10 000 кв. м начал работу на МКАД.',
                'full': '<p>Байкал-Сервис открыл новый современный терминал в Москве на 14-м километре МКАД. Площадь терминала составляет 10 000 квадратных метров, что позволяет обрабатывать до 500 тонн груза ежедневно.</p><p>Терминал оснащен автоматизированными линиями сортировки, современной погрузочной техникой и системой видеонаблюдения. Новый комплекс позволит значительно сократить время обработки грузов в московском регионе.</p>',
                'pub': now - timedelta(days=5),
            },
            {
                'title': 'Новый маршрут: Москва — Шанхай за 14 дней',
                'slug': 'new-route-moscow-shanghai',
                'short': 'Запущен новый мультимодальный маршрут доставки грузов из Москвы в Шанхай.',
                'full': '<p>Байкал-Сервис запускает новый мультимодальный маршрут Москва — Шанхай. Время в пути составляет всего 14 дней. Маршрут включает железнодорожную и автомобильную составляющие.</p><p>Новый маршрут позволяет российским предпринимателям быстро и выгодно доставлять товары из Китая. Стоимость перевозки от 35 рублей за килограмм.</p>',
                'pub': now - timedelta(days=12),
            },
            {
                'title': 'Итоги 2025 года: рекордные показатели',
                'slug': '2025-results',
                'short': 'По итогам 2025 года компания обработала более 1 миллиона отправлений.',
                'full': '<p>Байкал-Сервис подвел итоги 2025 года. Ключевые показатели: обработано более 1 000 000 отправлений, открыто 15 новых филиалов, запущено 3 новых международных маршрута.</p><p>Выручка компании выросла на 35% по сравнению с предыдущим годом. Количество корпоративных клиентов увеличилось на 40%. Компания продолжает активное развитие и расширение географии присутствия.</p>',
                'pub': now - timedelta(days=30),
            },
            {
                'title': 'Байкал-Сервис запускает мобильное приложение',
                'slug': 'mobile-app-launch',
                'short': 'Новое мобильное приложение для отслеживания грузов и управления заказами.',
                'full': '<p>Байкал-Сервис запускает мобильное приложение для iOS и Android. В приложении доступны: отслеживание грузов по трек-номеру, создание заказов, просмотр истории, оплата онлайн, связь с поддержкой.</p><p>Приложение уже доступно в App Store и Google Play. Отслеживать грузы теперь можно в одно касание!</p>',
                'pub': now - timedelta(days=45),
            },
            {
                'title': 'Партнерство с Wildberries: прямые поставки',
                'slug': 'wildberries-partnership',
                'short': 'Байкал-Сервис стал официальным партнером Wildberries по доставке.',
                'full': '<p>Байкал-Сервис заключил партнерское соглашение с Wildberries. Теперь продавцы Wildberries могут воспользоваться специальными условиями доставки товаров на склады маркетплейса.</p><p>Программа включает: бесплатный забор товара, приоритетную обработку, фиксированные тарифы от 22 рублей за кг.</p>',
                'pub': now - timedelta(days=60),
            },
            {
                'title': 'Расширение сети филиалов: новые города',
                'slug': 'new-branches-2025',
                'short': 'Байкал-Сервис открыл новые филиалы в 10 городах России.',
                'full': '<p>Байкал-Сервис продолжает расширение сети. В 2025 году открыты новые филиалы в 10 городах, включая Махачкалу, Грозный, Нальчик, Владикавказ, Майкоп, Черкесск, Элисту, Астрахань, Пензу и Тамбов.</p><p>Теперь сеть компании насчитывает более 80 собственных филиалов по всей России, в странах СНГ и Китае.</p>',
                'pub': now - timedelta(days=90),
            },
            {
                'title': 'Новый тариф «Посылка» для малого бизнеса',
                'slug': 'posylka-tariff-launch',
                'short': 'Запущен специальный тариф для отправки посылок весом до 20 кг.',
                'full': '<p>Байкал-Сервис запускает новый тариф «Посылка» для небольших отправлений. Тариф предназначен для малого бизнеса и частных лиц, которым нужно отправить посылку весом до 20 кг.</p><p>Стоимость отправки — от 350 рублей. Срок доставки — от 2 дней. Включено отслеживание по трек-номеру и SMS-уведомления.</p>',
                'pub': now - timedelta(days=120),
            },
            {
                'title': 'Байкал-Сервис на выставке TransRussia 2025',
                'slug': 'transrussia-2025',
                'short': 'Компания представила новые услуги на крупнейшей логистической выставке.',
                'full': '<p>Байкал-Сервис принял участие в выставке TransRussia 2025. На стенде компании были представлены новые услуги: технология «Имплант» для бесшовной интеграции, новые международные маршруты и мобильное приложение.</p><p>Стенд компании посетили более 500 потенциальных клиентов и партнеров.</p>',
                'pub': now - timedelta(days=150),
            },
            {
                'title': 'Экологическая инициатива: переход на электромобили',
                'slug': 'eco-initiative',
                'short': 'Байкал-Сервис начинает поэтапный переход на электротранспорт.',
                'full': '<p>Байкал-Сервис объявляет о запуске экологической программы. Компания начинает поэтапный перевод парка доставки на электромобили. Первые 50 электромобилей выйдут на линии в Москве и Санкт-Петербурге уже в этом году.</p><p>К 2030 году компания планирует перевести 70% городского парка на электротягу.</p>',
                'pub': now - timedelta(days=180),
            },
            {
                'title': 'Онлайн-калькулятор: новый сервис расчета стоимости',
                'slug': 'online-calculator',
                'short': 'Запущен обновленный онлайн-калькулятор с мгновенным расчетом стоимости.',
                'full': '<p>Байкал-Сервис запускает обновленный онлайн-калькулятор на сайте. Теперь рассчитать стоимость доставки можно за несколько кликов: укажите город отправления и назначения, вес и габариты груза — и получите точную стоимость.</p><p>Калькулятор учитывает все дополнительные услуги и показывает итоговую цену с учетом страховки, погрузочных работ и других опций.</p>',
                'pub': now - timedelta(days=200),
            },
        ]
        for n in news_items:
            NewsItem.objects.create(
                title=n['title'],
                title_en=n['title'],
                slug=n['slug'],
                short_text=n['short'],
                short_text_en=n['short'],
                full_text=n['full'],
                full_text_en=n['full'],
                published_at=n['pub'],
                is_published=True,
            )
        self.stdout.write(f'  Created {len(news_items)} news items')

    def _seed_faq(self):
        faqs = [
            # Shipping
            {'q': 'Как отправить груз через Байкал-Сервис?', 'a': 'Оформить заказ можно онлайн на нашем сайте, через мобильное приложение или обратившись в ближайший офис. Укажите город отправления и назначения, вес и габариты груза, выберите услуги и оплатите заказ.', 'cat': 'Отправка груза', 'order': 1},
            {'q': 'Какие документы нужны для отправки груза?', 'a': 'Для отправки груза физическому лицу нужен паспорт. Для юридических лиц — доверенность или печать организации. На груз оформляется транспортная накладная (ТН).', 'cat': 'Отправка груза', 'order': 2},
            {'q': 'Можно ли отправить груз без посещения офиса?', 'a': 'Да, вы можете заказать забор груза от двери. Курьер приедет по указанному адресу, заберет груз и оформит все необходимые документы на месте.', 'cat': 'Отправка груза', 'order': 3},
            {'q': 'Как упаковать груз для отправки?', 'a': 'Груз должен быть упакован в прочную тару, обеспечивающую сохранность при транспортировке. Мы предлагаем услуги упаковки: коробки, паллеты, стретч-пленка, обрешетка.', 'cat': 'Отправка груза', 'order': 4},
            # Tracking
            {'q': 'Как отследить груз?', 'a': 'Введите трек-номер на главной странице сайта или в мобильном приложении. Вы увидите текущий статус, все точки маршрута и примерную дату доставки.', 'cat': 'Отслеживание', 'order': 5},
            {'q': 'Что такое трек-номер и где его получить?', 'a': 'Трек-номер — это уникальный номер вашего отправления. Он присваивается автоматически при оформлении заказа и приходит на email и в SMS.', 'cat': 'Отслеживание', 'order': 6},
            {'q': 'Как часто обновляется статус груза?', 'a': 'Статус обновляется в реальном времени при прохождении каждой точки маршрута: приемка, склад, сортировка, погрузка, в пути, доставка.', 'cat': 'Отслеживание', 'order': 7},
            # Payment
            {'q': 'Какие способы оплаты доступны?', 'a': 'Мы принимаем: банковские карты (Visa, Mastercard, Мир), онлайн-оплату через сайт, безналичный расчет для юрлиц, наличные в офисе.', 'cat': 'Оплата', 'order': 8},
            {'q': 'Можно ли оплатить доставку после получения?', 'a': 'Да, для постоянных клиентов и корпоративных заказчиков доступна оплата с отсрочкой. Условия обсуждаются индивидуально.', 'cat': 'Оплата', 'order': 9},
            {'q': 'Как пополнить баланс в личном кабинете?', 'a': 'В разделе «Баланс» личного кабинета выберите сумму пополнения и способ оплаты. Средства зачисляются мгновенно.', 'cat': 'Оплата', 'order': 10},
            # Delivery
            {'q': 'Какие сроки доставки?', 'a': 'Сроки зависят от направления и выбранного тарифа. От 1 дня по России (экспресс) до 14 дней (международные). Точный расчет доступен в калькуляторе.', 'cat': 'Доставка', 'order': 11},
            {'q': 'Можно ли изменить адрес доставки?', 'a': 'Да, вы можете изменить адрес доставки до момента, когда груз передан в доставку по указанному адресу. Обратитесь в поддержку или измените данные в личном кабинете.', 'cat': 'Доставка', 'order': 12},
            {'q': 'Что делать, если груз поврежден?', 'a': 'При получении груза осмотрите его в присутствии водителя. В случае повреждений составьте акт. Обратитесь в службу поддержки для оформления претензии.', 'cat': 'Доставка', 'order': 13},
            # Documents
            {'q': 'Какие документы подтверждают доставку?', 'a': 'После доставки вы получаете: транспортную накладную с отметкой получателя, акт выполненных работ, счет-фактуру (для юрлиц).', 'cat': 'Документы', 'order': 14},
            {'q': 'Как получить электронные документы?', 'a': 'Электронные документы доступны в личном кабинете в разделе «Документы». Вы можете скачать их в любое время.', 'cat': 'Документы', 'order': 15},
            {'q': 'Как оформить доверенность на получение груза?', 'a': 'Доверенность оформляется в свободной форме с указанием паспортных данных получателя. Шаблон доступен на сайте в разделе «Документы».', 'cat': 'Документы', 'order': 16},
            # Insurance
            {'q': 'Нужно ли страховать груз?', 'a': 'Страхование груза — добровольная услуга. Рекомендуем страховать ценные и хрупкие грузы. Стоимость страховки — 3% от объявленной стоимости.', 'cat': 'Страхование', 'order': 17},
            {'q': 'Как оформить страховой случай?', 'a': 'При наступлении страхового случая обратитесь в службу поддержки в течение 3 дней. Предоставьте фото/видео повреждений и описание.', 'cat': 'Страхование', 'order': 18},
            # General
            {'q': 'Работаете ли вы с НДС?', 'a': 'Да, мы работаем с НДС. Юридическим лицам предоставляются все закрывающие документы: счет, акт, счет-фактура.', 'cat': 'Общие вопросы', 'order': 19},
            {'q': 'Как стать партнером Байкал-Сервис?', 'a': 'Заполните заявку в разделе «Партнерам». Мы рассматриваем заявки в течение 3 рабочих дней. Для партнеров действуют специальные условия сотрудничества.', 'cat': 'Общие вопросы', 'order': 20},
        ]
        objs = [FAQ(question=f['q'], question_en=f['q'], answer=f['a'], answer_en=f['a'], category=f['cat'], order=f['order'], is_published=True) for f in faqs]
        FAQ.objects.bulk_create(objs)
        self.stdout.write(f'  Created {len(objs)} FAQ entries')

    def _seed_reviews(self):
        reviews = [
            {'author': 'Иван Петров', 'company': 'ООО «ТехноПром»', 'text': 'Пользуюсь услугами Байкал-Сервис уже более 3 лет. Всегда вовремя, вежливые водители, адекватные цены. Отдельное спасибо за удобный личный кабинет.', 'rating': 5, 'source': 'Сайт'},
            {'author': 'Анна Смирнова', 'company': 'ИП Смирнова', 'text': 'Отличная компания! Отправляю посылки в разные города России. Всё приходит целым и в срок. Калькулятор на сайте очень удобный — сразу видишь стоимость.', 'rating': 5, 'source': 'Яндекс.Карты'},
            {'author': 'Сергей Кузнецов', 'company': 'АО «СтройМатериалы»', 'text': 'Работаем с Байкал-Сервис как корпоративный клиент. Выделенный менеджер всегда на связи, решает все вопросы оперативно. Рекомендуем!', 'rating': 5, 'source': 'Сайт'},
            {'author': 'Елена Васильева', 'company': 'ИП Васильева', 'text': 'Доставляю товары на Wildberries через Байкал-Сервис. Очень удобно и по цене приемлемо. Маркировка, сортировка — всё делают качественно.', 'rating': 5, 'source': 'Отзовик'},
            {'author': 'Дмитрий Соколов', 'company': 'Частное лицо', 'text': 'Отправлял посылку родителям в другой город. Всё просто: заказал на сайте, курьер забрал, через 3 дня уже доставили. Спасибо!', 'rating': 4, 'source': 'Сайт'},
            {'author': 'Ольга Федорова', 'company': 'ООО «МебельСтиль»', 'text': 'Возим мебель из Краснодара в Москву. Байкал-Сервис всегда аккуратно обрабатывает груз. Ни одного повреждения за год работы!', 'rating': 5, 'source': '2GIS'},
            {'author': 'Михаил Орлов', 'company': 'АО «ЭлектроСнаб»', 'text': 'Заказываем контейнерные перевозки из Китая. Байкал-Сервис отлично организует весь процесс: от забора на складе в Шанхае до доставки в Москву.', 'rating': 5, 'source': 'Сайт'},
            {'author': 'Татьяна Морозова', 'company': 'ООО «Книжный Мир»', 'text': 'Доставка книг по всей России. Байкал-Сервис надёжно упаковывает и быстро доставляет. Тариф «Посылка» очень выгодный для небольших грузов.', 'rating': 4, 'source': 'Яндекс.Карты'},
            {'author': 'Алексей Павлов', 'company': 'Частное лицо', 'text': 'Первый раз воспользовался услугой — всё понравилось. Цены адекватные, доставка быстрая. Буду пользоваться ещё.', 'rating': 4, 'source': 'Сайт'},
            {'author': 'Наталья Белова', 'company': 'ООО «ПродуктыПлюс»', 'text': 'Доставляем продукты в розничные сети. Байкал-Сервис понимает специфику — температурный режим соблюдается, документы оформляются правильно.', 'rating': 5, 'source': 'Отзовик'},
            {'author': 'Виктор Титов', 'company': 'ИП Титов', 'text': 'Пользуюсь услугой доставки на Ozon. Удобно, что можно сдать груз в любом филиале Байкал-Сервис. Терминалов много, всегда рядом.', 'rating': 5, 'source': 'Сайт'},
            {'author': 'Мария Ковалёва', 'company': 'АО «ТекстильТорг»', 'text': 'Работаем уже 2 года. Ни разу не подвели. Даже в пиковые сезоны справляются с объемами. Личный кабинет удобный, всё прозрачно.', 'rating': 5, 'source': 'Google'},
            {'author': 'Константин Зайцев', 'company': 'ООО «АвтоДеталь»', 'text': 'Отправляем автозапчасти в регионы. За год работы не было ни одной утерянной посылки. Спасибо команде Байкал-Сервис!', 'rating': 5, 'source': 'Сайт'},
            {'author': 'Екатерина Новикова', 'company': 'ИП Новикова', 'text': 'Очень довольна сервисом. Курьер всегда приезжает вовремя, грузы доставляются быстро. Цены радуют.', 'rating': 4, 'source': 'Яндекс.Карты'},
            {'author': 'Андрей Григорьев', 'company': 'ООО «ПромОборудование»', 'text': 'Заказывали авиадоставку оборудования из Москвы во Владивосток. Всё сделали за 2 дня! Дорого, но когда нужно срочно — лучший вариант.', 'rating': 5, 'source': 'Сайт'},
        ]
        objs = [Review(
            author_name=r['author'],
            author_company=r['company'],
            text=r['text'],
            rating=r['rating'],
            is_approved=True,
            source=r['source'],
            created_at=timezone.now() - timedelta(days=i * 5),
        ) for i, r in enumerate(reviews)]
        Review.objects.bulk_create(objs)
        self.stdout.write(f'  Created {len(objs)} reviews')

    def _seed_vacancies(self):
        moscow = City.objects.get(name='Москва')
        vacancies = [
            {
                'title': 'Водитель-экспедитор категории Е',
                'slug': 'driver-cat-e',
                'dept': 'Транспортный отдел',
                'city': moscow,
                'short': 'Требуется водитель-экспедитор с категорией Е для междугородних рейсов.',
                'full': '<p>Байкал-Сервис приглашает на работу водителей-экспедиторов категории Е. Работа на современных грузовых автомобилях Scania, MAN, Volvo. График работы: вахтовый метод, рейсы по России и СНГ.</p><p>Предоставляем полное медицинское страхование, оплачиваемое топливо и стоянки, премии за безаварийную работу.</p>',
                'req': '<ul><li>Категория Е (обязательно)</li><li>Стаж вождения от 3 лет</li><li>Наличие карты тахографа</li><li>Ответственность и дисциплина</li></ul>',
                'from': 80000,
                'to': 120000,
            },
            {
                'title': 'Менеджер по работе с клиентами',
                'slug': 'account-manager',
                'dept': 'Отдел продаж',
                'city': moscow,
                'short': 'Ищем опытного менеджера по работе с корпоративными клиентами.',
                'full': '<p>В связи с расширением отдела продаж, мы ищем менеджера по работе с корпоративными клиентами. Вы будете сопровождать клиентов на всех этапах сотрудничества: от презентации до отправки груза.</p><p>Мы предлагаем: конкурентную зарплату, KPI и бонусы за результат, обучение за счет компании, карьерный рост.</p>',
                'req': '<ul><li>Опыт работы в логистике от 1 года</li><li>Навыки ведения переговоров</li><li>Уверенное владение CRM</li><li>Высшее образование (желательно)</li></ul>',
                'from': 60000,
                'to': 100000,
            },
            {
                'title': 'Бухгалтер',
                'slug': 'accountant',
                'dept': 'Бухгалтерия',
                'city': moscow,
                'short': 'Требуется бухгалтер с опытом работы в транспортной компании.',
                'full': '<p>В бухгалтерию Байкал-Сервис требуется бухгалтер с опытом работы от 2 лет. Знание 1С обязательно. Мы предлагаем стабильную работу в крупной компании, полный соцпакет, дружный коллектив.</p>',
                'req': '<ul><li>Высшее экономическое образование</li><li>Опыт работы от 2 лет</li><li>Знание 1С:Бухгалтерия</li><li>Знание налогового законодательства</li></ul>',
                'from': 65000,
                'to': 90000,
            },
            {
                'title': 'Логист',
                'slug': 'logistician',
                'dept': 'Логистический отдел',
                'city': moscow,
                'short': 'Ищем логиста для планирования и контроля маршрутов доставки.',
                'full': '<p>В отдел логистики требуется специалист по планированию маршрутов и контролю перевозок. Вы будете координировать автопарк, оптимизировать маршруты, взаимодействовать с водителями и клиентами.</p><p>Мы предлагаем работу в современном офисе, молодой коллектив, возможности для обучения и развития.</p>',
                'req': '<ul><li>Опыт работы логистом от 1 года</li><li>Навыки работы с картами и маршрутами</li><li>Стрессоустойчивость</li><li>Умение работать в режиме многозадачности</li></ul>',
                'from': 55000,
                'to': 85000,
            },
            {
                'title': 'IT-специалист (Python/Django)',
                'slug': 'it-specialist',
                'dept': 'IT-отдел',
                'city': moscow,
                'short': 'Требуется Python/Django разработчик для развития внутренних систем.',
                'full': '<p>IT-отдел Байкал-Сервис приглашает Python-разработчика для работы над внутренними системами, сайтом и интеграциями. У нас современный стек: Django, DRF, PostgreSQL, React, Docker, CI/CD.</p><p>Мы предлагаем: удаленную работу или работу в офисе, гибкий график, современное оборудование, профессиональное развитие, оплату курсов и конференций.</p>',
                'req': '<ul><li>Python от 2 лет</li><li>Django/DRF</li><li>PostgreSQL</li><li>Git, Linux</li><li>Желательно: React, Docker</li></ul>',
                'from': 120000,
                'to': 200000,
            },
        ]
        for v in vacancies:
            Vacancy.objects.create(
                title=v['title'],
                title_en=v['title'],
                slug=v['slug'],
                department=v['dept'],
                city=v['city'],
                short_description=v['short'],
                full_description=v['full'],
                requirements=v['req'],
                salary_from=v['from'],
                salary_to=v['to'],
                is_active=True,
                published_at=timezone.now() - timedelta(days=10),
            )
        self.stdout.write(f'  Created {len(vacancies)} vacancies')

    def _seed_promotions(self):
        now = timezone.now()
        promos = [
            {
                'title': 'Скидка 20% на первую отправку',
                'slug': 'first-shipment-discount',
                'short': 'Для новых клиентов — скидка 20% на первую отправку груза.',
                'full': '<p>Станьте клиентом Байкал-Сервис и получите скидку 20% на первую отправку! Акция действует для всех новых клиентов, оформивших заказ через сайт или мобильное приложение.</p><p>Скидка распространяется на все тарифы, кроме экспресс-доставки. Минимальная сумма заказа — 1 000 рублей.</p>',
                'start': now,
                'end': now + timedelta(days=90),
            },
            {
                'title': 'Бесплатный забор груза',
                'slug': 'free-pickup',
                'short': 'Закажите доставку от 5 000 ₽ и получите забор груза бесплатно.',
                'full': '<p>При заказе доставки на сумму от 5 000 рублей забор груза от отправителя — бесплатно! Акция действует во всех городах присутствия Байкал-Сервис.</p><p>Предложение не суммируется с другими акциями и скидками.</p>',
                'start': now,
                'end': now + timedelta(days=60),
            },
            {
                'title': 'Летние скидки на авиадоставку',
                'slug': 'summer-air-discount',
                'short': 'Скидка 15% на авиаперевозки по всем направлениям.',
                'full': '<p>Лето — время путешествий и скидок! Получите скидку 15% на авиадоставку грузов по России. Акция действует на все направления.</p><p>Минимальный вес груза — 5 кг. Максимальный — 100 кг. Спешите, количество мест ограничено!</p>',
                'start': now + timedelta(days=30),
                'end': now + timedelta(days=120),
            },
            {
                'title': 'Тариф «Посылка» — от 350 ₽',
                'slug': 'posylka-promo',
                'short': 'Отправляйте посылки до 20 кг от 350 ₽ по всей России.',
                'full': '<p>Специальное предложение на тариф «Посылка»! Отправляйте небольшие грузы весом до 20 кг по фиксированным ценам: до 5 кг — 350 ₽, до 10 кг — 550 ₽, до 20 кг — 850 ₽.</p><p>В стоимость включено отслеживание по трек-номеру и SMS-уведомления.</p>',
                'start': now,
                'end': now + timedelta(days=180),
            },
            {
                'title': 'Для корпоративных клиентов: персональные условия',
                'slug': 'corporate-offer',
                'short': 'Специальные тарифы для бизнеса при объеме от 50 отправлений в месяц.',
                'full': '<p>Корпоративным клиентам мы предлагаем персональные условия сотрудничества: индивидуальные тарифы, персонального менеджера, отсрочку платежа, ежемесячные отчеты, приоритетную обработку грузов.</p><p>Оставьте заявку на сайте, и наш менеджер свяжется с вами для обсуждения условий.</p>',
                'start': now,
                'end': now + timedelta(days=365),
            },
        ]
        for p in promos:
            Promotion.objects.create(
                title=p['title'],
                title_en=p['title'],
                slug=p['slug'],
                short_description=p['short'],
                full_description=p['full'],
                start_date=p['start'],
                end_date=p['end'],
                is_active=True,
            )
        self.stdout.write(f'  Created {len(promos)} promotions')

    def _seed_tenders(self):
        now = timezone.now()
        tenders = [
            {
                'title': 'Поставка автомобильных шин для грузового транспорта',
                'slug': 'tires-supply',
                'desc': '<p>Байкал-Сервис объявляет открытый тендер на поставку автомобильных шин для грузового транспорта. Требуется поставка 500 комплектов шин для тягачей и полуприцепов.</p><p>Участники тендера должны предоставить коммерческое предложение, сертификаты качества и опыт работы от 3 лет.</p>',
                'deadline': now + timedelta(days=30),
            },
            {
                'title': 'Разработка мобильного приложения',
                'slug': 'mobile-app-dev',
                'desc': '<p>Байкал-Сервис ищет подрядчика для разработки мобильного приложения на iOS и Android. Приложение должно включать: отслеживание грузов, создание заказов, оплату, чат с поддержкой.</p><p>Желаемый стек: React Native или Flutter. Срок разработки — 6 месяцев. Бюджет — от 3 млн рублей.</p>',
                'deadline': now + timedelta(days=45),
            },
            {
                'title': 'Услуги по уборке терминалов',
                'slug': 'cleaning-services',
                'desc': '<p>Тендер на оказание услуг по профессиональной уборке терминалов Байкал-Сервис в Москве. Общая площадь уборки — 15 000 кв. м. Требуется ежедневная уборка и вывоз мусора.</p><p>Договор заключается на 1 год с возможностью продления. Заявки принимаются до указанного срока.</p>',
                'deadline': now + timedelta(days=60),
            },
        ]
        for t in tenders:
            Tender.objects.create(
                title=t['title'],
                slug=t['slug'],
                description=t['desc'],
                deadline=t['deadline'],
                is_active=True,
            )
        self.stdout.write(f'  Created {len(tenders)} tenders')

    def _seed_partner_data(self):
        Banner.objects.create(
            title='Скидка 20% на первую отправку',
            link='/promotions/first-shipment-discount/',
            placement='header',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=90),
            is_active=True,
        )
        Banner.objects.create(
            title='Бесплатный забор груза',
            link='/promotions/free-pickup/',
            placement='sidebar',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=60),
            is_active=True,
        )
        Banner.objects.create(
            title='Тариф «Посылка» от 350 ₽',
            link='/services/posylka-tariff/',
            placement='footer',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=180),
            is_active=True,
        )

        IframeModule.objects.create(
            name='Калькулятор доставки',
            description='Интерактивный калькулятор для расчета стоимости доставки',
            embed_code='<iframe src="https://baikal-service.ru/tools/calculator/embed/" width="100%" height="400" frameborder="0"></iframe>',
            documentation='<p>Вставьте код на свой сайт для отображения калькулятора доставки. Ширина адаптируется автоматически.</p>',
        )
        IframeModule.objects.create(
            name='Отслеживание груза',
            description='Виджет для отслеживания груза по трек-номеру',
            embed_code='<iframe src="https://baikal-service.ru/tracking/embed/" width="100%" height="200" frameborder="0"></iframe>',
            documentation='<p>Вставьте код на свой сайт для отображения формы отслеживания грузов.</p>',
        )

        PartnerApplication.objects.create(
            company_name='ООО «ЛогистикПлюс»',
            contact_person='Иван Петров',
            email='ivan@logisticplus.ru',
            phone='+7 (495) 111-22-33',
            website='https://logisticplus.ru',
            status='new',
        )
        PartnerApplication.objects.create(
            company_name='ИП Сидоров А.В.',
            contact_person='Антон Сидоров',
            email='anton@example.ru',
            phone='+7 (916) 555-66-77',
            website='',
            status='reviewing',
        )

        self.stdout.write('  Created banners, iframe modules, partner apps')

    def _seed_documents(self):
        docs = [
            {'title': 'Договор транспортной экспедиции', 'cat': 'contracts', 'desc': 'Типовой договор транспортной экспедиции для юридических лиц'},
            {'title': 'Заявка на перевозку груза', 'cat': 'shipping_docs', 'desc': 'Форма заявки на перевозку груза'},
            {'title': 'Транспортная накладная (ТН)', 'cat': 'shipping_docs', 'desc': 'Стандартная форма транспортной накладной'},
            {'title': 'Товарно-транспортная накладная (ТТН)', 'cat': 'shipping_docs', 'desc': 'Форма товарно-транспортной накладной 1-Т'},
            {'title': 'Акт приема-передачи груза', 'cat': 'receipt_docs', 'desc': 'Акт приема-передачи груза при доставке'},
            {'title': 'Доверенность на получение груза', 'cat': 'power_of_attorney', 'desc': 'Шаблон доверенности на получение груза'},
            {'title': 'Претензия о повреждении груза', 'cat': 'claims', 'desc': 'Форма претензии при повреждении груза'},
            {'title': 'Заявление на возврат', 'cat': 'refunds', 'desc': 'Форма заявления на возврат денежных средств'},
        ]
        objs = [Document(title=d['title'], title_en=d['title'], category=d['cat'], description=d['desc'], is_active=True) for d in docs]
        Document.objects.bulk_create(objs)
        self.stdout.write(f'  Created {len(objs)} documents')

    def _seed_superuser(self):
        if not CustomUser.objects.filter(email='admin@baikal-service.ru').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@baikal-service.ru',
                password='admin123',
                phone='+7 (495) 000-00-00',
                role='admin',
            )
            self.stdout.write('  Created superuser admin@baikal-service.ru / admin123')
        else:
            self.stdout.write('  Superuser already exists, skipped')
