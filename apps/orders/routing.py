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


def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_route(from_city, to_city):
    if not from_city or not to_city:
        return {'type': 'unknown', 'warehouse_stop': None, 'delivery_days': 3}

    distance = haversine_distance(from_city.latitude, from_city.longitude, to_city.latitude, to_city.longitude)

    nearby_threshold = 500.0
    is_nearby = distance < nearby_threshold

    warehouse = get_nearest_warehouse(from_city)
    if warehouse:
        warehouse_dist = haversine_distance(warehouse.latitude, warehouse.longitude, to_city.latitude, to_city.longitude)
    else:
        warehouse_dist = float('inf')

    if is_nearby and warehouse_dist > distance:
        base_days = max(1, int(distance / 200))
        return {
            'type': 'direct',
            'warehouse_stop': None,
            'delivery_days': base_days,
        }

    if warehouse:
        warehouse_days = max(1, int(distance / 300)) + 1
        return {
            'type': 'via_warehouse',
            'warehouse_stop': warehouse,
            'delivery_days': warehouse_days,
        }

    base_days = max(1, int(distance / 200))
    return {
        'type': 'direct',
        'warehouse_stop': None,
        'delivery_days': base_days,
    }


def calculate_price(from_city, to_city, weight, service=None, additional_services=None, declared_value=None):
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
        if base_price == 0 or price < base_price:
            base_price = price
            tariff_used = tariff

    if base_price == 0 and service and service.base_price:
        base_price = service.base_price * Decimal(str(weight))

    if base_price == 0:
        base_price = Decimal(str(weight)) * Decimal('50')

    branch_in_city = has_branch_in_city(from_city)
    if not branch_in_city:
        base_price = (base_price * SURCHARGE_MULTIPLIER).quantize(Decimal('0.01'))

    if route.get('warehouse_stop'):
        handling_fee = Decimal('500')
        base_price += handling_fee

    additional_total = Decimal('0')
    if additional_services:
        for add_svc in additional_services.all():
            if add_svc.price_type == 'fixed':
                additional_total += add_svc.price
            elif add_svc.price_type == 'per_unit':
                additional_total += add_svc.price * Decimal(str(weight))
            elif add_svc.price_type == 'percentage' and declared_value:
                additional_total += (add_svc.price / Decimal('100')) * Decimal(str(declared_value))

    total_price = base_price + additional_total

    delivery_days = route['delivery_days']
    if tariff_used:
        delivery_days = random.randint(tariff_used.delivery_days_min, tariff_used.delivery_days_max)

    return {
        'base_price': base_price.quantize(Decimal('0.01')),
        'additional_services_price': additional_total.quantize(Decimal('0.01')),
        'total_price': total_price.quantize(Decimal('0.01')),
        'route': route,
        'tariff': tariff_used,
        'surcharge_applied': not branch_in_city,
        'delivery_days': delivery_days,
    }


def get_next_statuses(current_status):
    status_flow = {
        'draft': ['confirmed'],
        'confirmed': ['picked_up'],
        'awaiting_delivery_to_branch': ['picked_up'],
        'available_in_warehouse': ['picked_up'],
        'awaiting_courier': ['picked_up'],
        'picked_up': ['in_transit'],
        'in_transit': ['at_warehouse', 'out_for_delivery'],
        'at_warehouse': ['out_for_delivery'],
        'out_for_delivery': ['delivered'],
        'delivered': [],
        'cancelled': [],
    }
    return status_flow.get(current_status, [])


def get_initial_status(from_city):
    if from_city is None:
        return 'draft'
    if has_warehouse_in_city(from_city):
        return 'awaiting_delivery_to_branch'
    elif has_branch_in_city(from_city):
        return 'available_in_warehouse'
    return 'awaiting_courier'


def compute_eta(from_city, to_city, delivery_days=None):
    if delivery_days is None:
        route = calculate_route(from_city, to_city)
        days = route['delivery_days']
        if route.get('warehouse_stop'):
            days += 1
    else:
        days = delivery_days
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
    raw_progress = (elapsed / total_seconds) * 100

    status_progress = {
        'confirmed': (0, 10),
        'picked_up': (5, 25),
        'in_transit': (20, 85),
        'at_warehouse': (50, 75),
        'awaiting_delivery_to_branch': (15, 40),
        'available_in_warehouse': (15, 40),
        'awaiting_courier': (15, 40),
        'out_for_delivery': (85, 100),
    }
    lo, hi = status_progress.get(current_status, (0, 100))
    status_progress = lo + (hi - lo) * min(1.0, raw_progress / 100.0)
    base_progress = max(0, min(100, status_progress))

    seed = created_at.timestamp() + (now.hour % 5) * 7.1
    rng = random.Random(seed)
    deviation = rng.uniform(-5, 5)

    progress = max(0, min(100, base_progress + deviation))

    route_deviation = math.sin(progress / 100 * math.pi * 3) * 0.02

    lat = from_city.latitude + (to_city.latitude - from_city.latitude) * (progress / 100)
    lng = from_city.longitude + (to_city.longitude - from_city.longitude) * (progress / 100)
    lat += route_deviation * (to_city.longitude - from_city.longitude)
    lng += route_deviation * (from_city.latitude - to_city.latitude)

    lat = max(min(from_city.latitude, to_city.latitude), min(max(from_city.latitude, to_city.latitude), lat))
    lng = max(min(from_city.longitude, to_city.longitude), min(max(from_city.longitude, to_city.longitude), lng))

    return {'lat': round(lat, 6), 'lng': round(lng, 6), 'progress': round(progress, 1)}
