from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Name (EN)'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    icon = models.CharField(max_length=100, blank=True, verbose_name=_('Icon'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    description_en = models.TextField(blank=True, verbose_name=_('Description (EN)'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name=_('Parent category'))

    class Meta:
        verbose_name = _('Service category')
        verbose_name_plural = _('Service categories')
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_localized_name(self, language='ru'):
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name

    def get_localized_description(self, language='ru'):
        if language == 'en' and self.description_en:
            return self.description_en
        return self.description


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name=_('Category'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Name (EN)'))
    slug = models.SlugField(verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    description_en = models.TextField(blank=True, verbose_name=_('Description (EN)'))
    short_description = models.CharField(max_length=500, blank=True, verbose_name=_('Short description'))
    short_description_en = models.CharField(max_length=500, blank=True, verbose_name=_('Short description (EN)'))
    icon = models.CharField(max_length=100, blank=True, verbose_name=_('Icon'))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Base price'))
    price_unit = models.CharField(max_length=50, blank=True, verbose_name=_('Price unit'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Sort order'))

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ['sort_order']
        unique_together = [('category', 'slug')]

    def __str__(self):
        return self.name

    def get_localized_name(self, language='ru'):
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name

    def get_localized_description(self, language='ru'):
        if language == 'en' and self.description_en:
            return self.description_en
        return self.description

    def get_localized_short_description(self, language='ru'):
        if language == 'en' and self.short_description_en:
            return self.short_description_en
        return self.short_description


class AdditionalService(models.Model):
    class PriceType(models.TextChoices):
        FIXED = 'fixed', _('Fixed')
        PER_UNIT = 'per_unit', _('Per unit')
        PERCENTAGE = 'percentage', _('Percentage')

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Name (EN)'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    description_en = models.TextField(blank=True, verbose_name=_('Description (EN)'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    price_type = models.CharField(max_length=20, choices=PriceType.choices, default=PriceType.FIXED, verbose_name=_('Price type'))

    class Meta:
        verbose_name = _('Additional service')
        verbose_name_plural = _('Additional services')

    def __str__(self):
        return self.name

    def get_localized_name(self, language='ru'):
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name

    def get_localized_description(self, language='ru'):
        if language == 'en' and self.description_en:
            return self.description_en
        return self.description


class Tariff(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Name (EN)'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    description_en = models.TextField(blank=True, verbose_name=_('Description (EN)'))
    min_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Min weight (kg)'))
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Max weight (kg)'))
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price per kg'))
    delivery_days_min = models.IntegerField(verbose_name=_('Min delivery days'))
    delivery_days_max = models.IntegerField(verbose_name=_('Max delivery days'))

    class Meta:
        verbose_name = _('Tariff')
        verbose_name_plural = _('Tariffs')

    def __str__(self):
        return self.name

    def get_localized_name(self, language='ru'):
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name

    def get_localized_description(self, language='ru'):
        if language == 'en' and self.description_en:
            return self.description_en
        return self.description
