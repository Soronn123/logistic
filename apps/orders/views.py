import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, TemplateView, View

from apps.geo.models import City

from .forms import OrderForm
from .models import Order, OrderStatusHistory
from .routing import (
    calculate_price,
    compute_eta,
    compute_virtual_location,
    get_initial_status,
    get_next_statuses,
    has_branch_in_city,
)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'pages/orders/create.html'
    success_url = reverse_lazy('users:orders')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.services.models import AdditionalService, Service
        cities_qs = City.objects.filter(is_active=True)
        context['cities'] = cities_qs
        context['services'] = Service.objects.filter(is_active=True)
        context['additional_services'] = AdditionalService.objects.all()
        context['cities_json'] = json.dumps([
            {
                'id': c.id,
                'name': str(c),
                'latitude': c.latitude,
                'longitude': c.longitude,
            }
            for c in cities_qs
        ])
        context['default_lat'] = 55.7558
        context['default_lng'] = 37.6173
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        from_city = form.cleaned_data.get('sender_address')
        to_city = form.cleaned_data.get('recipient_address')
        weight = form.cleaned_data.get('weight') or 0
        service = form.cleaned_data.get('service')

        pricing = calculate_price(from_city, to_city, float(weight), service)
        form.instance.total_price = pricing['total_price']
        form.instance.status = get_initial_status(from_city)
        form.instance.estimated_delivery_date = compute_eta(from_city, to_city)

        response = super().form_valid(form)

        OrderStatusHistory.objects.create(
            order=self.object,
            status=self.object.status,
            changed_by=self.request.user,
            comment=_('Order created'),
        )

        simulate_cargo_transport(self.object)
        self.object.refresh_from_db()

        messages.success(
            self.request,
            _('Order %(tracking)s created successfully! You can track it in your orders.') % {
                'tracking': self.object.tracking_number,
            },
        )

        return response


class OrderTrackView(DetailView):
    model = Order
    template_name = 'pages/orders/track.html'
    context_object_name = 'order'
    slug_field = 'tracking_number'
    slug_url_kwarg = 'tracking_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.select_related('changed_by').order_by('timestamp')
        return context


def simulate_cargo_transport(order):
    from_city = order.sender_address
    to_city = order.recipient_address
    if not from_city or not to_city:
        return

    route = calculate_price(from_city, to_city, float(order.weight or 1), order.service)
    delivery_days = route.get('delivery_days', 3)
    has_warehouse = route.get('route', {}).get('warehouse_stop') is not None

    now = timezone.now()
    status_order = ['confirmed', 'picked_up', 'in_transit']
    if has_warehouse:
        status_order.append('at_warehouse')
    status_order.append('out_for_delivery')
    status_order.append('delivered')

    initial_status = get_initial_status(from_city)
    if initial_status in [s[0] for s in Order.Status.choices]:
        status_order = [initial_status] + [s for s in status_order if s != initial_status]

    existing = set(order.status_history.values_list('status', flat=True))
    status_order = [s for s in status_order if s not in existing]

    if not status_order:
        return

    day_fractions = [i / len(status_order) for i in range(1, len(status_order) + 1)]

    for i, status in enumerate(status_order):
        offset_days = delivery_days * day_fractions[i]
        simulated_time = now + timedelta(days=offset_days * 0.5)

        comment_map = {
            'confirmed': _('Order confirmed and registered'),
            'picked_up': _('Cargo picked up from sender'),
            'in_transit': _('Cargo in transit to destination'),
            'at_warehouse': _('Cargo arrived at sorting warehouse'),
            'out_for_delivery': _('Cargo out for delivery to recipient'),
            'delivered': _('Cargo delivered successfully'),
            'awaiting_delivery_to_branch': _('Awaiting delivery to branch'),
            'available_in_warehouse': _('Cargo available at warehouse'),
            'awaiting_courier': _('Awaiting courier pickup'),
        }

        OrderStatusHistory.objects.create(
            order=order,
            status=status,
            changed_by=order.user,
            comment=comment_map.get(status, status),
            timestamp=simulated_time,
        )

    order.status = status_order[-1]
    if order.status == 'delivered':
        order.actual_delivery_date = now.date() + timedelta(days=int(delivery_days * 0.5))
    order.save(update_fields=['status', 'actual_delivery_date'])


class TrackingLookupView(TemplateView):
    template_name = 'pages/orders/tracking_lookup.html'

    def get(self, request, *args, **kwargs):
        tracking_number = request.GET.get('tracking_number', '').strip()
        if tracking_number:
            order = get_object_or_404(Order, tracking_number=tracking_number)
            return render(request, 'pages/orders/track.html', {
                'order': order,
                'status_history': order.status_history.select_related('changed_by').order_by('timestamp'),
            })
        return super().get(request, *args, **kwargs)


class TrackingPublicDetailView(DetailView):
    model = Order
    template_name = 'pages/orders/track.html'
    context_object_name = 'order'
    slug_field = 'tracking_number'
    slug_url_kwarg = 'tracking_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.select_related('changed_by').order_by('timestamp')
        return context


class DoorDeliveryRequestView(TemplateView):
    template_name = 'pages/orders/door_delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_number'] = self.kwargs.get('tracking_number', '')
        return context


class RequestChangesView(TemplateView):
    template_name = 'pages/orders/request_changes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_number'] = self.kwargs.get('tracking_number', '')
        return context
