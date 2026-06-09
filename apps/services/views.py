from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _

from apps.services.models import ServiceCategory, Service, AdditionalService, Tariff


class ServiceCategoryListView(ListView):
    model = ServiceCategory
    template_name = 'pages/services/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return ServiceCategory.objects.filter(parent__isnull=True).prefetch_related('children', 'services')


class ServiceCategoryDetailView(DetailView):
    model = ServiceCategory
    template_name = 'pages/services/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.services.filter(is_active=True)
        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'pages/services/service_detail.html'
    context_object_name = 'service'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Service.objects.select_related('category'),
            category__slug=self.kwargs['category_slug'],
            slug=self.kwargs['slug'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object.category
        return context


class AdditionalServiceListView(ListView):
    model = AdditionalService
    template_name = 'pages/services/additionalservice_list.html'
    context_object_name = 'services'


class TariffListView(ListView):
    model = Tariff
    template_name = 'pages/services/tariff_list.html'
    context_object_name = 'tariffs'
