from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, TemplateView, View

from .forms import OrderForm
from .models import Order, OrderStatusHistory
from .routing import calculate_price, compute_eta, get_initial_status, has_branch_in_city
from apps.geo.models import City


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
        from apps.geo.models import City
        from apps.services.models import AdditionalService, Service
        context['cities'] = City.objects.filter(is_active=True).distinct()
        context['services'] = Service.objects.filter(is_active=True).distinct()
        context['additional_services'] = AdditionalService.objects.all().distinct()
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

        return response


class OrderTrackView(DetailView):
    model = Order
    template_name = 'pages/orders/track.html'
    context_object_name = 'order'
    slug_field = 'tracking_number'
    slug_url_kwarg = 'tracking_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.select_related('changed_by')
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
