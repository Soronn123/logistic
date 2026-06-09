import math
import random
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

SURCHARGE_MULTIPLIER = Decimal('1.3')


def has_branch_in_city(city):
    from apps.geo.models import Branch
    return Branch.objects.filter(city=city, is_active=True).exists()


def has_warehouse_in_city(city):
    from apps.geo.models import Branch
    return Branch.objects.filter(city=city, branch_type='warehouse', is_active=True).exists()


def get_nearest_warehouse(city):
    from apps.geo.models import Branch
    return Branch.objects.filter(
        branch_type='warehouse', is_active=True
    ).select_related('city').first()


def calculate_route(from_city, to_city):
    if not from_city or not to_city:
        return {'type': 'unknown', 'warehouse_stop': None, 'delivery_days': 3}

    from_lat, from_lng = from_city.latitude, from_city.longitude
    to_lat, to_lng = to_city.latitude, to_city.longitude

    distance = math.sqrt((to_lat - from_lat) ** 2 + (to_lng - from_lng) ** 2)

    nearby_threshold = 5.0
    is_nearby = distance < nearby_threshold

    warehouse = get_nearest_warehouse(from_city)
    if warehouse:
        warehouse_dist = math.sqrt(
            (warehouse.latitude - to_lat) ** 2 + (warehouse.longitude - to_lng) ** 2
        )
    else:
        warehouse_dist = float('inf')

    if is_nearby and warehouse_dist > distance:
        base_days = max(1, int(distance * 2))
        return {
            'type': 'direct',
            'warehouse_stop': None,
            'delivery_days': base_days,
        }

    if warehouse:
        warehouse_days = max(1, int(distance * 1.5)) + 1
        return {
            'type': 'via_warehouse',
            'warehouse_stop': warehouse,
            'delivery_days': warehouse_days,
        }

    base_days = max(1, int(distance * 2))
    return {
        'type': 'direct',
        'warehouse_stop': None,
        'delivery_days': base_days,
    }


def calculate_price(from_city, to_city, weight, service=None):
    from apps.services.models import Tariff

    route = calculate_route(from_city, to_city)

    tariffs = Tariff.objects.filter(
        min_weight__lte=weight
    ).filter(
        max_weight__gte=weight
    ) | Tariff.objects.filter(
        min_weight__lte=weight, max_weight__isnull=True
    )

    base_price = Decimal('0')
    tariff_used = None
    for tariff in tariffs:
        price = Decimal(str(tariff.price_per_kg)) * Decimal(str(weight))
        if price > base_price:
            base_price = price
            tariff_used = tariff

    if base_price == 0 and service and service.base_price:
        base_price = service.base_price * Decimal(str(weight))

    if base_price == 0:
        base_price = Decimal(str(weight)) * Decimal('50')

    if not has_branch_in_city(from_city):
        base_price = (base_price * SURCHARGE_MULTIPLIER).quantize(Decimal('0.01'))

    if route.get('warehouse_stop'):
        handling_fee = Decimal('500')
        base_price += handling_fee

    return {
        'base_price': base_price.quantize(Decimal('0.01')),
        'total_price': base_price.quantize(Decimal('0.01')),
        'route': route,
        'tariff': tariff_used,
        'surcharge_applied': not has_branch_in_city(from_city),
        'delivery_days': route['delivery_days'],
    }


def get_next_statuses(current_status):
    status_flow = {
        'draft': ['confirmed'],
        'confirmed': ['picked_up'],
        'picked_up': ['in_transit'],
        'in_transit': ['at_warehouse', 'out_for_delivery'],
        'at_warehouse': ['out_for_delivery'],
        'out_for_delivery': ['delivered'],
        'delivered': [],
        'cancelled': [],
    }
    return status_flow.get(current_status, [])


def get_initial_status(from_city):
    if has_warehouse_in_city(from_city):
        return 'awaiting_delivery_to_branch'
    elif has_branch_in_city(from_city):
        return 'available_in_warehouse'
    return 'awaiting_courier'


def compute_eta(from_city, to_city):
    route = calculate_route(from_city, to_city)
    days = route['delivery_days']
    if route.get('warehouse_stop'):
        days += 1
    return timezone.now().date() + timedelta(days=days)


def compute_virtual_location(from_city, to_city, eta, created_at, current_status):
    if current_status in ('delivered', 'cancelled'):
        return {'lat': to_city.latitude, 'lng': to_city.longitude, 'progress': 100}

    if current_status == 'draft':
        return {'lat': from_city.latitude, 'lng': from_city.longitude, 'progress': 0}

    now = timezone.now()
    if eta is None:
        return {'lat': from_city.latitude, 'lng': from_city.longitude, 'progress': 0}
    total_seconds = (eta - created_at.date()).total_seconds()
    if total_seconds <= 0:
        return {'lat': to_city.latitude, 'lng': to_city.longitude, 'progress': 100}

    elapsed = (now - created_at).total_seconds()
    base_progress = min(100, (elapsed / total_seconds) * 100)

    probability = random.random()
    if probability < 0.33:
        deviation = random.uniform(-15, -5)
    elif probability < 0.66:
        deviation = random.uniform(5, 15)
    else:
        deviation = random.uniform(-3, 3)

    progress = max(0, min(100, base_progress + deviation))

    lat = from_city.latitude + (to_city.latitude - from_city.latitude) * (progress / 100)
    lng = from_city.longitude + (to_city.longitude - from_city.longitude) * (progress / 100)

    return {'lat': lat, 'lng': lng, 'progress': round(progress, 1)}