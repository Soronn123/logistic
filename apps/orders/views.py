import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, TemplateView, View

from apps.geo.models import City

from .forms import OrderForm
from .models import Order, OrderStatusHistory
from .routing import (
    auto_assign_services,
    calculate_price,
    compute_eta,
    get_initial_status,
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
        from apps.documents.models import Document
        from apps.services.models import AdditionalService, Service
        cities_qs = City.objects.filter(is_active=True)
        context['cities'] = cities_qs
        services = Service.objects.filter(is_active=True).prefetch_related('documents')
        context['services'] = services
        context['additional_services'] = AdditionalService.objects.filter(is_active=True).prefetch_related('documents')
        context['cities_json'] = json.dumps([
            {
                'id': c.id,
                'name': str(c),
                'latitude': c.latitude,
                'longitude': c.longitude,
                'country': c.country,
            }
            for c in cities_qs
        ])
        context['default_lat'] = 55.7558
        context['default_lng'] = 37.6173

        context['user_balance'] = float(self.request.user.balance or 0)

        # Compute auto-assignment rules for display on the services step
        context['auto_service_slugs'] = {
            'customs_duty': 'customs-duty',
            'customs_clearance': 'customs-clearance',
            'warehouse_transit': 'warehouse-transit',
            'last_mile_delivery': 'last-mile-delivery',
            'email_order_created': 'email-order-created',
            'email_customs_cleared': 'email-customs-cleared',
            'email_delivered': 'email-delivered',
            'extended_insurance': 'extended-insurance',
            'hand_carry': 'hand-carry',
            'adr_transport': 'adr-transport',
            'refrigerated_transport': 'refrigerated-transport',
            'truck_transport': 'truck-transport',
            'rail_transport': 'rail-transport',
        }

        # Build document mappings for template
        docs_qs = Document.objects.filter(is_active=True).prefetch_related('services', 'additional_services')
        service_docs = {}
        addon_docs = {}
        for doc in docs_qs:
            for svc in doc.services.all():
                service_docs.setdefault(svc.id, []).append({
                    'id': doc.id,
                    'title': doc.title,
                    'category': doc.get_category_display(),
                    'url': doc.file.url if doc.file else None,
                })
            for addon in doc.additional_services.all():
                addon_docs.setdefault(addon.id, []).append({
                    'id': doc.id,
                    'title': doc.title,
                    'category': doc.get_category_display(),
                    'url': doc.file.url if doc.file else None,
                })
        context['service_documents_json'] = json.dumps(service_docs)
        context['addon_documents_json'] = json.dumps(addon_docs)

        return context

    def form_valid(self, form):
        # Prevent duplicate submissions
        session_key = 'order_create_timestamp'
        current_time = timezone.now().timestamp()
        last_create_time = self.request.session.get(session_key, 0)

        # If an order was created less than 5 seconds ago, reject this submission
        if current_time - last_create_time < 5:
            messages.error(self.request, _('Please wait before creating another order.'))
            return self.form_invalid(form)

        form.instance.user = self.request.user

        from_city = form.cleaned_data.get('sender_address')
        to_city = form.cleaned_data.get('recipient_address')
        weight = form.cleaned_data.get('weight') or 0
        service = form.cleaned_data.get('service')
        additional_services = form.cleaned_data.get('additional_services')
        declared_value = form.cleaned_data.get('declared_value')
        is_fragile = form.cleaned_data.get('is_fragile', False)
        is_dangerous = form.cleaned_data.get('is_dangerous', False)
        is_temperature_sensitive = form.cleaned_data.get('is_temperature_sensitive', False)

        # Auto-assign services based on cargo and route rules
        auto = auto_assign_services(
            from_city=from_city,
            to_city=to_city,
            weight=float(weight),
            length=form.cleaned_data.get('length'),
            width=form.cleaned_data.get('width'),
            height=form.cleaned_data.get('height'),
            declared_value=declared_value,
            is_fragile=is_fragile,
            is_dangerous=is_dangerous,
            is_temperature_sensitive=is_temperature_sensitive,
        )

        # Apply auto-assigned service if user didn't select one
        if not service and auto.get('service'):
            form.instance.service = auto['service']

        # Set additional services (merge user-selected with auto-assigned)
        user_addons = list(additional_services.all()) if additional_services else []
        auto_addons = auto.get('additional_services', [])
        all_addons = user_addons + [a for a in auto_addons if a not in user_addons]

        pricing = calculate_price(
            from_city, to_city, float(weight), form.instance.service or service,
            additional_services=all_addons,
            declared_value=declared_value,
        )
        form.instance.total_price = pricing['total_price']
        form.instance.status = get_initial_status(from_city)
        form.instance.estimated_delivery_date = compute_eta(
            from_city, to_city, delivery_days=pricing['delivery_days']
        )

        user = self.request.user
        total = pricing['total_price']

        if user.balance < total:
            form.add_error(None, _('Insufficient balance. Your balance is %(balance)s ₽, but the order total is %(total)s ₽. Please top up your balance.') % {
                'balance': user.balance,
                'total': total,
            })
            return self.form_invalid(form)

        response = super().form_valid(form)

        # Update session to prevent duplicate submissions
        self.request.session['order_create_timestamp'] = timezone.now().timestamp()

        # Deduct balance
        user.balance -= total
        user.save(update_fields=['balance'])
        from apps.users.models import Transaction
        Transaction.objects.create(
            user=user,
            amount=-total,
            transaction_type=Transaction.TransactionType.WITHDRAWAL,
            description=_('Payment for order %(tracking)s') % {'tracking': self.object.tracking_number},
            balance_after=user.balance,
        )

        # Set additional services after save (m2m)
        if all_addons:
            self.object.additional_services.set(all_addons)

        OrderStatusHistory.objects.create(
            order=self.object,
            status=self.object.status,
            changed_by=self.request.user,
            comment=_('Order created'),
        )

        from .routing import send_status_notification
        send_status_notification(self.object)

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
        context['attached_documents'] = self.object.get_attached_documents()
        return context


class TrackingLookupView(TemplateView):
    template_name = 'pages/orders/tracking_lookup.html'

    def get(self, request, *args, **kwargs):
        tracking_number = request.GET.get('tracking_number', '').strip()
        if tracking_number:
            order = get_object_or_404(Order, tracking_number=tracking_number)
            return render(request, 'pages/orders/track.html', {
                'order': order,
                'status_history': order.status_history.select_related('changed_by').order_by('timestamp'),
                'attached_documents': order.get_attached_documents(),
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
        context['attached_documents'] = self.object.get_attached_documents()
        return context


class DoorDeliveryRequestView(TemplateView):
    template_name = 'pages/orders/door_delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_number'] = self.kwargs.get('tracking_number', '')
        return context


class RequestChangesView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/orders/request_changes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, tracking_number=self.kwargs.get('tracking_number'))
        if order.user != self.request.user:
            messages.error(self.request, _('You can only request changes for your own orders.'))
            return redirect('orders:track', tracking_number=self.kwargs.get('tracking_number'))
        context['order'] = order
        context['change_requests'] = order.status_history.filter(
            comment__startswith='[Change Request]'
        ).order_by('-timestamp')
        return context

    def post(self, request, tracking_number):
        order = get_object_or_404(Order, tracking_number=tracking_number)
        if order.user != request.user:
            messages.error(request, _('You can only request changes for your own orders.'))
            return redirect('orders:track', tracking_number=tracking_number)

        message = request.POST.get('message', '').strip()

        if not message:
            messages.error(request, _('Please describe the changes you need.'))
            return redirect('orders:request_changes', tracking_number=tracking_number)

        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,
            changed_by=request.user,
            comment=_('[Change Request] %(message)s') % {'message': message},
        )

        messages.success(request, _('Your change request has been submitted.'))
        return redirect('orders:track', tracking_number=tracking_number)
