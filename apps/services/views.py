from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _

from apps.services.models import ServiceCategory, Service, AdditionalService, Tariff


class ServiceCategoryListView(ListView):
    model = ServiceCategory
    template_name = 'pages/services/category_list.html'
    context_object_name = 'categories'
    paginate_by = 12

    def get_queryset(self):
        active_services = Service.objects.filter(is_active=True)
        qs = ServiceCategory.objects.filter(parent__isnull=True).prefetch_related(
            Prefetch('services', queryset=active_services),
            Prefetch('children', queryset=ServiceCategory.objects.all()),
        )
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(name_en__icontains=q) | Q(description__icontains=q)
            )
        else:
            qs = qs.filter(services__is_active=True).distinct()
        return qs


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

    def get_queryset(self):
        return AdditionalService.objects.filter(is_active=True)


class TariffListView(ListView):
    model = Tariff
    template_name = 'pages/services/tariff_list.html'
    context_object_name = 'tariffs'
