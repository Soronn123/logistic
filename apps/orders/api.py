from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View

from .models import Order, OrderStatusHistory
from .routing import compute_virtual_location, get_next_statuses


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