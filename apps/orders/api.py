import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Order, OrderStatusHistory
from .routing import compute_virtual_location, get_next_statuses
from apps.users.models import ContactTemplate, CargoTemplate, DeliveryTemplate


class OrderStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, tracking_number):
        order = get_object_or_404(Order, tracking_number=tracking_number, user=request.user)
        new_status = request.POST.get('status')

        allowed = get_next_statuses(order.status)
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

        return JsonResponse({
            'status': new_status,
            'old_status': old_status,
            'tracking_number': order.tracking_number,
        })


class OrderPickupConfirmView(LoginRequiredMixin, View):
    def post(self, request, tracking_number):
        order = get_object_or_404(Order, tracking_number=tracking_number, user=request.user)

        if order.status not in ('awaiting_delivery_to_branch', 'available_in_warehouse', 'awaiting_courier', 'confirmed'):
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
            return JsonResponse({'error': _('Cannot confirm delivery in current status')}, status=400)

        if not is_recipient and order.user != request.user:
            return JsonResponse({'error': _('Only the recipient can confirm delivery')}, status=400)

        if order.status == 'out_for_delivery':
            old_status = order.status
            order.status = 'delivered'
            order.actual_delivery_date = __import__('django').utils.timezone.now().date()
            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                status='delivered',
                changed_by=request.user,
                comment=_('Delivery confirmed by recipient'),
            )

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
            'sender_city': str(order.sender_address),
            'recipient_city': str(order.recipient_address),
            'estimated_delivery': str(order.estimated_delivery_date or ''),
            'actual_delivery': str(order.actual_delivery_date or ''),
            'current_location': location,
            'total_price': float(order.total_price) if order.total_price else 0,
            'history': list(order.status_history.values('status', 'timestamp', 'comment')),
        }
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class ContactTemplateListView(LoginRequiredMixin, View):
    def get(self, request):
        template_type = request.GET.get('type', 'recipient')
        templates = ContactTemplate.objects.filter(
            user=request.user, template_type=template_type
        ).values('id', 'name', 'recipient_name', 'recipient_phone', 'recipient_email', 'city', 'address_detail')
        return JsonResponse(list(templates), safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': _('Invalid JSON')}, status=400)

        name = data.get('name', '').strip()
        template_type = data.get('template_type', 'recipient')
        if not name:
            return JsonResponse({'error': _('Template name is required')}, status=400)

        template = ContactTemplate.objects.create(
            user=request.user,
            name=name,
            template_type=template_type,
            recipient_name=data.get('contact_name', ''),
            recipient_phone=data.get('contact_phone', ''),
            recipient_email=data.get('contact_email', ''),
            city_id=data.get('city'),
            address_detail=data.get('address_detail', ''),
        )
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'template_type': template.template_type,
            'recipient_name': template.recipient_name,
            'recipient_phone': template.recipient_phone,
            'recipient_email': template.recipient_email,
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


@method_decorator(csrf_exempt, name='dispatch')
class DeliveryTemplateListView(LoginRequiredMixin, View):
    def get(self, request):
        templates = DeliveryTemplate.objects.filter(user=request.user).values(
            'id', 'name', 'from_city', 'to_city', 'weight', 'cargo_description', 'service',
            'declared_value', 'sender_address_detail', 'recipient_address_detail', 'total_price'
        )
        templates_list = list(templates)
        for tpl in templates_list:
            dt = DeliveryTemplate.objects.get(id=tpl['id'])
            tpl['additional_services'] = list(dt.additional_services.values_list('id', flat=True))
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
            from_city_id=data.get('from_city'),
            to_city_id=data.get('to_city'),
            weight=data.get('weight', 0),
            cargo_description=data.get('cargo_description', ''),
            service_id=data.get('service'),
            declared_value=data.get('declared_value'),
            sender_address_detail=data.get('sender_address_detail', ''),
            recipient_address_detail=data.get('recipient_address_detail', ''),
            total_price=data.get('total_price'),
        )
        addon_ids = data.get('additional_services', [])
        if addon_ids:
            from apps.services.models import AdditionalService
            template.additional_services.set(AdditionalService.objects.filter(id__in=addon_ids))
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'from_city': template.from_city_id,
            'to_city': template.to_city_id,
            'weight': str(template.weight),
            'cargo_description': template.cargo_description,
            'service': template.service_id,
            'declared_value': str(template.declared_value or ''),
            'sender_address_detail': template.sender_address_detail,
            'recipient_address_detail': template.recipient_address_detail,
            'additional_services': list(template.additional_services.values_list('id', flat=True)),
            'total_price': str(template.total_price or ''),
        })


class DeliveryTemplateDetailView(LoginRequiredMixin, View):
    def put(self, request, pk):
        template = get_object_or_404(DeliveryTemplate, pk=pk, user=request.user)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': _('Invalid JSON')}, status=400)

        template.name = data.get('name', template.name)
        if data.get('from_city'):
            template.from_city_id = data.get('from_city')
        if data.get('to_city'):
            template.to_city_id = data.get('to_city')
        template.weight = data.get('weight', template.weight)
        template.cargo_description = data.get('cargo_description', template.cargo_description)
        if data.get('service'):
            template.service_id = data.get('service')
        template.declared_value = data.get('declared_value', template.declared_value)
        template.sender_address_detail = data.get('sender_address_detail', template.sender_address_detail)
        template.recipient_address_detail = data.get('recipient_address_detail', template.recipient_address_detail)
        template.total_price = data.get('total_price', template.total_price)
        template.save()
        addon_ids = data.get('additional_services')
        if addon_ids is not None:
            from apps.services.models import AdditionalService
            template.additional_services.set(AdditionalService.objects.filter(id__in=addon_ids))
        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'from_city': template.from_city_id,
            'to_city': template.to_city_id,
            'weight': str(template.weight),
            'cargo_description': template.cargo_description,
            'service': template.service_id,
            'declared_value': str(template.declared_value or ''),
            'sender_address_detail': template.sender_address_detail,
            'recipient_address_detail': template.recipient_address_detail,
            'additional_services': list(template.additional_services.values_list('id', flat=True)),
            'total_price': str(template.total_price or ''),
        })

    def delete(self, request, pk):
        template = get_object_or_404(DeliveryTemplate, pk=pk, user=request.user)
        template.delete()
        return JsonResponse({'deleted': True})


@method_decorator(csrf_exempt, name='dispatch')
class CargoTemplateListView(LoginRequiredMixin, View):
    def get(self, request):
        templates = CargoTemplate.objects.filter(user=request.user).values(
            'id', 'name', 'cargo_description', 'weight', 'length', 'width', 'height', 'declared_value'
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
        })


class CargoTemplateDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        template = get_object_or_404(CargoTemplate, pk=pk, user=request.user)
        template.delete()
        return JsonResponse({'deleted': True})