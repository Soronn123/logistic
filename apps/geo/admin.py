from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import City, Branch, BranchImage


class BranchImageInline(admin.TabularInline):
    model = BranchImage
    extra = 0


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    fields = ['branch_type', 'address', 'phone', 'is_active']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'is_active', 'timezone']
    list_filter = ['is_active', 'region']
    search_fields = ['name', 'name_en', 'region', 'region_en']
    inlines = [BranchInline]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['city', 'address', 'branch_type', 'phone', 'is_active']
    list_filter = ['branch_type', 'is_active', 'city']
    search_fields = ['city__name', 'address', 'address_en', 'phone']
    inlines = [BranchImageInline]


@admin.register(BranchImage)
class BranchImageAdmin(admin.ModelAdmin):
    list_display = ['branch', 'caption', 'order']
    search_fields = ['branch__city__name', 'caption']
    list_editable = ['order']
