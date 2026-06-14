import logging
import math
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

# Slugs for auto-assignment — matching seed data in services app
CUSTOMS_DUTY_SLUG = 'customs-duty'
CUSTOMS_CLEARANCE_SLUG = 'customs-clearance'
WAREHOUSE_TRANSIT_SLUG = 'warehouse-transit'
LAST_MILE_DELIVERY_SLUG = 'last-mile-delivery'
EMAIL_ORDER_CREATED_SLUG = 'email-order-created'
EMAIL_CUSTOMS_CLEARED_SLUG = 'email-customs-cleared'
EMAIL_DELIVERED_SLUG = 'email-delivered'
EXTENDED_INSURANCE_SLUG = 'extended-insurance'
HAND_CARRY_SLUG = 'hand-carry'
ADR_TRANSPORT_SLUG = 'adr-transport'
REFRIGERATED_TRANSPORT_SLUG = 'refrigerated-transport'
TRUCK_TRANSPORT_SLUG = 'truck-transport'
RAIL_TRANSPORT_SLUG = 'rail-transport'


def auto_assign_services(from_city, to_city, weight, length, width, height,
                         declared_value, is_fragile=False, is_dangerous=False,
                         is_temperature_sensitive=False):
    """
    Auto-assign main service and additional services based on cargo and route.

    Returns dict with keys:
      - service: Service instance or None
      - additional_services: list of AdditionalService instances
    """
    from apps.services.models import AdditionalService, Service

    assigned_additional = []

    # Determine if international
    is_international = (
        from_city and to_city
        and getattr(from_city, 'country', 'RU') != getattr(to_city, 'country', 'RU')
    )

    # Check if direct route exists
    route = calculate_route(from_city, to_city)
    has_direct_route = route['type'] == 'direct'

    # Check warehouse/PVZ in destination city
    has_warehouse_dest = has_warehouse_in_city(to_city) if to_city else False

    # Check dimensions for air transport restriction
    weight_ok = float(weight) <= 80
    dims = [d for d in [length, width, height] if d]
    dims_ok = all(float(d) <= 120 for d in dims) if dims else True
    can_use_air = weight_ok and dims_ok

    def _get_addon(slug):
        try:
            return AdditionalService.objects.get(slug=slug)
        except AdditionalService.DoesNotExist:
            return None

    def _get_service(slug):
        return Service.objects.filter(slug=slug, is_active=True).first()

    # --- Rule 1: International → customs duty + customs clearance ---
    if is_international:
        for slug in (CUSTOMS_DUTY_SLUG, CUSTOMS_CLEARANCE_SLUG):
            svc = _get_addon(slug)
            if svc:
                assigned_additional.append(svc)

    # --- Rule 2: No direct route → warehouse transit ---
    if not has_direct_route:
        svc = _get_addon(WAREHOUSE_TRANSIT_SLUG)
        if svc:
            assigned_additional.append(svc)

    # --- Rule 3: No warehouse/PVZ in destination → last-mile delivery ---
    if to_city and not has_warehouse_dest:
        svc = _get_addon(LAST_MILE_DELIVERY_SLUG)
        if svc:
            assigned_additional.append(svc)

    # --- Rules 4 & 5: Email notifications ---
    if is_international:
        for slug in (EMAIL_ORDER_CREATED_SLUG, EMAIL_CUSTOMS_CLEARED_SLUG, EMAIL_DELIVERED_SLUG):
            svc = _get_addon(slug)
            if svc:
                assigned_additional.append(svc)
    else:
        for slug in (EMAIL_ORDER_CREATED_SLUG, EMAIL_DELIVERED_SLUG):
            svc = _get_addon(slug)
            if svc:
                assigned_additional.append(svc)

    # --- Rule 6: Oversize/overweight → no air, use truck or rail ---
    auto_service = None
    if not can_use_air:
        auto_service = _get_service(TRUCK_TRANSPORT_SLUG) or _get_service(RAIL_TRANSPORT_SLUG)
    else:
        # Default: try to get air transport or first available service
        auto_service = _get_service('air-transport') or _get_service(TRUCK_TRANSPORT_SLUG)

    # --- Rule 7: Declared value > 50 000 ₽ → extended insurance ---
    if declared_value and float(declared_value) > 50000:
        svc = _get_addon(EXTENDED_INSURANCE_SLUG)
        if svc:
            assigned_additional.append(svc)

    # --- Rule 8: Fragile → careful handling (Hand Carry) ---
    if is_fragile:
        svc = _get_addon(HAND_CARRY_SLUG)
        if svc:
            assigned_additional.append(svc)

    # --- Rule 9: Dangerous goods → ADR transport ---
    if is_dangerous:
        svc = _get_addon(ADR_TRANSPORT_SLUG)
        if svc:
            assigned_additional.append(svc)

    # --- Rule 10: Temperature-sensitive → refrigerated transport ---
    if is_temperature_sensitive:
        svc = _get_addon(REFRIGERATED_TRANSPORT_SLUG)
        if svc:
            assigned_additional.append(svc)

    return {
        'service': auto_service,
        'additional_services': assigned_additional,
    }


def has_branch_in_city(city):
    from apps.geo.models import Branch
    return Branch.objects.filter(city=city, is_active=True).exists()


def has_warehouse_in_city(city):
    from apps.geo.models import Branch
    return Branch.objects.filter(city=city, branch_type='warehouse', is_active=True).exists()


def get_nearest_warehouse(city):
    from apps.geo.models import Branch
    if city:
        return Branch.objects.filter(
            city=city, branch_type='warehouse', is_active=True
        ).select_related('city').first()
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

    if route.get('warehouse_stop'):
        handling_fee = Decimal('500')
        base_price += handling_fee

    additional_total = Decimal('0')
    if additional_services:
        addon_iter = additional_services.all() if hasattr(additional_services, 'all') else additional_services
        for add_svc in addon_iter:
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
        'delivery_days': delivery_days,
    }


def get_next_statuses(current_status, is_international=False):
    status_flow = {
        'draft': ['confirmed'],
        'confirmed': ['picked_up'],
        'awaiting_delivery_to_branch': ['picked_up'],
        'available_in_warehouse': ['picked_up'],
        'awaiting_courier': ['picked_up'],
        'picked_up': ['in_transit'],
        'in_transit': ['customs_clearance', 'at_warehouse', 'out_for_delivery'] if is_international else ['at_warehouse', 'out_for_delivery'],
        'customs_clearance': ['at_warehouse', 'out_for_delivery'],
        'at_warehouse': ['out_for_delivery'],
        'out_for_delivery': ['delivered'],
        'delivered': [],
        'cancelled': [],
    }
    return status_flow.get(current_status, [])


SIMULATION_INTERVALS = {
    ('draft', 'confirmed'): 120,
    ('confirmed', 'awaiting_delivery_to_branch'): 60,
    ('confirmed', 'awaiting_courier'): 60,
    ('awaiting_delivery_to_branch', 'available_in_warehouse'): 180,
    ('available_in_warehouse', 'picked_up'): 120,
    ('awaiting_courier', 'picked_up'): 300,
    ('picked_up', 'in_transit'): 600,
    ('in_transit', 'customs_clearance'): 3600,
    ('in_transit', 'at_warehouse'): 1800,
    ('customs_clearance', 'at_warehouse'): 1800,
    ('at_warehouse', 'out_for_delivery'): 300,
    ('out_for_delivery', 'delivered'): 600,
}


def get_simulation_flow(order):
    """Return the full ordered list of statuses for simulation, given an order."""
    from_city = order.sender_address
    to_city = order.recipient_address
    has_branch = has_branch_in_city(from_city) if from_city else False

    is_international = (
        from_city and to_city
        and getattr(from_city, 'country', 'RU') != getattr(to_city, 'country', 'RU')
    )
    flow = ['draft', 'confirmed']
    if has_branch:
        flow.extend(['awaiting_delivery_to_branch', 'available_in_warehouse'])
    else:
        flow.append('awaiting_courier')
    flow.append('picked_up')
    flow.append('in_transit')
    if is_international:
        flow.append('customs_clearance')
    flow.extend(['at_warehouse', 'out_for_delivery', 'delivered'])
    return flow


def simulate_next_status(order):
    """Return the next status to advance to in simulation, or None if complete."""
    flow = get_simulation_flow(order)
    try:
        idx = flow.index(order.status)
        if idx + 1 < len(flow):
            return flow[idx + 1]
    except ValueError:
        pass
    return None


def get_simulation_interval(current_status, next_status):
    """Return minimum seconds to wait between status transitions."""
    return SIMULATION_INTERVALS.get((current_status, next_status), 300)


def get_initial_status(from_city):
    if from_city is None:
        return 'draft'
    if has_branch_in_city(from_city):
        return 'awaiting_delivery_to_branch'
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
    if not from_city or not to_city:
        return {'lat': 0, 'lng': 0, 'progress': 0}

    if current_status in ('delivered', 'cancelled'):
        return {'lat': to_city.latitude, 'lng': to_city.longitude, 'progress': 100}

    if current_status == 'draft':
        return {'lat': from_city.latitude, 'lng': from_city.longitude, 'progress': 0}

    now = timezone.now()
    if eta is None:
        return {'lat': from_city.latitude, 'lng': from_city.longitude, 'progress': 0}

    if created_at.tzinfo is None:
        created_at = timezone.make_aware(created_at)
    if now.tzinfo is None:
        now = timezone.make_aware(now)

    eta_dt = timezone.make_aware(datetime.combine(eta, datetime.min.time()))
    total_seconds = (eta_dt - created_at).total_seconds()
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


def send_status_notification(order, old_status=None):
    """Send email notification when order status changes."""
    if not order.sender_email and not order.recipient_email:
        return

    from apps.orders.models import Order
    status_labels = dict(Order.Status.choices)
    subject = _('Order %(tracking)s — %(status)s') % {
        'tracking': order.tracking_number,
        'status': status_labels.get(order.status, order.status),
    }

    context = {
        'order': order,
        'status': status_labels.get(order.status, order.status),
        'old_status': status_labels.get(old_status, old_status) if old_status else None,
        'tracking_url': f'{settings.SITE_URL}/tracking/{order.tracking_number}/' if hasattr(settings, 'SITE_URL') else '',
    }

    try:
        html_message = render_to_string('emails/status_notification.html', context)
        text_message = _('Status of order %(tracking)s changed to: %(status)s') % {
            'tracking': order.tracking_number,
            'status': status_labels.get(order.status, order.status),
        }

        recipients = []
        if order.sender_email:
            recipients.append(order.sender_email)
        if order.recipient_email and order.recipient_email != order.sender_email:
            recipients.append(order.recipient_email)

        if recipients:
            send_mail(subject, text_message, settings.DEFAULT_FROM_EMAIL, recipients, html_message=html_message)
    except Exception as e:
        logger.error('Failed to send status notification for %s: %s', order.tracking_number, e)
