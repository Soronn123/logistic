import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View

from .models import Order, OrderStatusHistory
from .routing import compute_virtual_location, get_next_statuses
from apps.users.models import ContactTemplate, CargoTemplate, DeliveryTemplate


class OrderStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, tracking_number):
        if not (request.user.is_staff or request.user.role in ('admin', 'manager')):
            return JsonResponse({'error': _('Only staff can update order status')}, status=403)
        order = get_object_or_404(Order, tracking_number=tracking_number)
        new_status = request.POST.get('status')

        is_international = (
            order.sender_address and order.recipient_address
            and order.sender_address.country != order.recipient_address.country
        )
        allowed = get_next_statuses(order.status, is_international=is_international)
        if new_status not in allowed:
            return JsonResponse({'error': _('Invalid status transition')}, status=400)

        old_status = order.status
        order.status = new_status
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            changed_by=request.user,
            comment=request.POST.get('comment', ''),
        )

        from .routing import send_status_notification
        send_status_notification(order, old_status=old_status)

        return JsonResponse({
            'status': new_status,
            'old_status': old_status,
            'tracking_number': order.tracking_number,
        })


class OrderPickupConfirmView(LoginRequiredMixin, View):
    def post(self, request, tracking_number):
        order = get_object_or_404(Order, tracking_number=tracking_number, user=request.user)

        if order.status not in ('awaiting_delivery_to_branch', 'available_in_warehouse', 'awaiting_courier', 'confirmed'):
            if request.accepts('text/html'):
                messages.error(request, _('Cannot confirm pickup in current status.'))
                return redirect('orders:track', tracking_number=tracking_number)
            return JsonResponse({'error': _('Cannot confirm pickup in current status')}, status=400)

        old_status = order.status
        order.status = 'picked_up'
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status='picked_up',
            changed_by=request.user,
            comment=_('Cargo picked up by carrier'),
        )

        from .routing import send_status_notification
        send_status_notification(order, old_status=old_status)

        if request.accepts('text/html'):
            messages.success(request, _('Cargo pickup confirmed.'))
            return redirect('orders:track', tracking_number=tracking_number)

        return JsonResponse({
            'status': 'picked_up',
            'old_status': old_status,
            'tracking_number': order.tracking_number,
        })


class OrderDeliveryConfirmView(LoginRequiredMixin, View):
    def post(self, request, tracking_number):
        order = get_object_or_404(Order, tracking_number=tracking_number, user=request.user)

        is_recipient = (
            request.user.phone == order.recipient_phone
            or request.user.email == order.recipient_email
        )

        if order.status != 'out_for_delivery' and order.status != 'delivered':
            if request.accepts('text/html'):
                messages.error(request, _('Cannot confirm delivery in current status.'))
                return redirect('orders:track', tracking_number=tracking_number)
            return JsonResponse({'error': _('Cannot confirm delivery in current status')}, status=400)

        if not is_recipient and order.user != request.user:
            if request.accepts('text/html'):
                messages.error(request, _('Only the recipient can confirm delivery.'))
                return redirect('orders:track', tracking_number=tracking_number)
            return JsonResponse({'error': _('Only the recipient can confirm delivery')}, status=400)

        if order.status == 'out_for_delivery':
            old_status = order.status
            order.status = 'delivered'
            order.actual_delivery_date = timezone.now().date()
            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                status='delivered',
                changed_by=request.user,
                comment=_('Delivery confirmed by recipient'),
            )

            from .routing import send_status_notification
            send_status_notification(order, old_status=old_status)

        if request.accepts('text/html'):
            messages.success(request, _('Delivery confirmed successfully.'))
            return redirect('orders:track', tracking_number=tracking_number)

        return JsonResponse({
            'status': 'delivered',
            'tracking_number': order.tracking_number,
        })


class OrderTrackingAPIView(View):
    def get(self, request, tracking_number):
        order = get_object_or_404(Order, tracking_number=tracking_number)

        location = compute_virtual_location(
            order.sender_address, order.recipient_address,
            order.estimated_delivery_date, order.created_at, order.status
        )

        data = {
            'tracking_number': order.tracking_number,
            'status': order.status,
            'status_label': order.get_status_display(),
            'sender_city': str(order.sender_address) if order.sender_address else '',
            'recipient_city': str(order.recipient_address) if order.recipient_address else '',
            'estimated_delivery': str(order.estimated_delivery_date or ''),
            'actual_delivery': str(order.actual_delivery_date or ''),
            'current_location': location,
            'total_price': float(order.total_price) if order.total_price else 0,
            'history': list(order.status_history.values('status', 'timestamp', 'comment')),
        }
        return JsonResponse(data)


class ContactTemplateListView(LoginRequiredMixin, View):
    def get(self, request):
        templates = ContactTemplate.objects.filter(
            user=request.user
        ).values('id', 'name', 'contact_name', 'contact_phone', 'contact_email',
                 'city', 'address_detail')
        return JsonResponse(list(templates), safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': _('Invalid JSON')}, status=400)

        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': _('Template name is required')}, status=400)

        template = ContactTemplate.objects.create(
            user=request.user,
            name=name,
            contact_name=data.get('contact_name', ''),
            contact_phone=data.get('contact_phone', ''),
            contact_email=data.get('contact_email', ''),
            city_id=data.get('city'),
            address_detail=data.get('address_detail', ''),
        )
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'contact_name': template.contact_name,
            'contact_phone': template.contact_phone,
            'contact_email': template.contact_email,
            'city': template.city_id,
            'address_detail': template.address_detail,
        })


class ContactTemplateDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        template = get_object_or_404(ContactTemplate, pk=pk, user=request.user)
        template.delete()
        return JsonResponse({'deleted': True})


class AddressSuggestView(View):
    def get(self, request):
        return JsonResponse({'suggestions': []})


class DeliveryTemplateListView(LoginRequiredMixin, View):
    def get(self, request):
        templates_qs = DeliveryTemplate.objects.filter(user=request.user).prefetch_related('additional_services')
        templates_list = []
        for dt in templates_qs:
            templates_list.append({
                'id': dt.id,
                'name': dt.name,
                'service': dt.service_id,
                'additional_services': list(dt.additional_services.values_list('id', flat=True)),
            })
        return JsonResponse(templates_list, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': _('Invalid JSON')}, status=400)

        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': _('Template name is required')}, status=400)

        template = DeliveryTemplate.objects.create(
            user=request.user,
            name=name,
            service_id=data.get('service'),
        )
        addon_ids = data.get('additional_services', [])
        if addon_ids:
            from apps.services.models import AdditionalService
            template.additional_services.set(AdditionalService.objects.filter(id__in=addon_ids))
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'service': template.service_id,
            'additional_services': list(template.additional_services.values_list('id', flat=True)),
        })


class DeliveryTemplateDetailView(LoginRequiredMixin, View):
    def put(self, request, pk):
        template = get_object_or_404(DeliveryTemplate, pk=pk, user=request.user)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': _('Invalid JSON')}, status=400)

        template.name = data.get('name', template.name)
        if data.get('service'):
            template.service_id = data.get('service')
        template.save()
        addon_ids = data.get('additional_services')
        if addon_ids is not None:
            from apps.services.models import AdditionalService
            template.additional_services.set(AdditionalService.objects.filter(id__in=addon_ids))
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'service': template.service_id,
            'additional_services': list(template.additional_services.values_list('id', flat=True)),
        })

    def delete(self, request, pk):
        template = get_object_or_404(DeliveryTemplate, pk=pk, user=request.user)
        template.delete()
        return JsonResponse({'deleted': True})


class CargoTemplateListView(LoginRequiredMixin, View):
    def get(self, request):
        templates = CargoTemplate.objects.filter(user=request.user).values(
            'id', 'name', 'cargo_description', 'weight', 'length', 'width', 'height', 'declared_value',
            'is_fragile', 'is_dangerous', 'is_temperature_sensitive'
        )
        return JsonResponse(list(templates), safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': _('Invalid JSON')}, status=400)

        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': _('Template name is required')}, status=400)

        template = CargoTemplate.objects.create(
            user=request.user,
            name=name,
            cargo_description=data.get('cargo_description', ''),
            weight=data.get('weight', 0),
            length=data.get('length'),
            width=data.get('width'),
            height=data.get('height'),
            declared_value=data.get('declared_value'),
            is_fragile=data.get('is_fragile', False),
            is_dangerous=data.get('is_dangerous', False),
            is_temperature_sensitive=data.get('is_temperature_sensitive', False),
        )
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'cargo_description': template.cargo_description,
            'weight': str(template.weight),
            'length': str(template.length or ''),
            'width': str(template.width or ''),
            'height': str(template.height or ''),
            'declared_value': str(template.declared_value or ''),
            'is_fragile': template.is_fragile,
            'is_dangerous': template.is_dangerous,
            'is_temperature_sensitive': template.is_temperature_sensitive,
        })


class CargoTemplateDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        template = get_object_or_404(CargoTemplate, pk=pk, user=request.user)
        template.delete()
        return JsonResponse({'deleted': True})