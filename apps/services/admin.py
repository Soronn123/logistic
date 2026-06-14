from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.documents.models import Document
from .models import ServiceCategory, Service, AdditionalService, Tariff


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ['name', 'slug', 'sort_order', 'is_active']


class ServiceDocumentInline(admin.TabularInline):
    model = Document.services.through
    extra = 0
    verbose_name = _('Document')
    verbose_name_plural = _('Documents')


class AdditionalServiceDocumentInline(admin.TabularInline):
    model = Document.additional_services.through
    extra = 0
    verbose_name = _('Document')
    verbose_name_plural = _('Documents')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'icon']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'price_unit', 'sort_order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['sort_order', 'is_active']
    inlines = [ServiceDocumentInline]


@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'price_type']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AdditionalServiceDocumentInline]


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_weight', 'max_weight', 'price_per_kg', 'delivery_days_min', 'delivery_days_max']
    search_fields = ['name', 'description']
