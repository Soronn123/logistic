from django.db import models
from django.utils.translation import gettext_lazy as _


class City(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Name (EN)'))
    region = models.CharField(max_length=255, blank=True, verbose_name=_('Region'))
    region_en = models.CharField(max_length=255, blank=True, verbose_name=_('Region (EN)'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    timezone = models.CharField(max_length=50, blank=True, verbose_name=_('Timezone'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['name']

    def get_localized_name(self, language='ru'):
        if language == 'en' and self.name_en:
            return self.name_en
        return self.name

    def __str__(self):
        return self.name


class Branch(models.Model):
    class BranchType(models.TextChoices):
        WAREHOUSE = 'warehouse', _('Warehouse')
        PICKUP_POINT = 'pickup_point', _('Pickup point')
        OFFICE = 'office', _('Office')

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='branches', verbose_name=_('City'))
    branch_type = models.CharField(max_length=20, choices=BranchType.choices, verbose_name=_('Branch type'))
    address = models.CharField(max_length=500, verbose_name=_('Address'))
    address_en = models.CharField(max_length=500, blank=True, verbose_name=_('Address (EN)'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    working_hours = models.JSONField(blank=True, default=dict, verbose_name=_('Working hours'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    has_pickup = models.BooleanField(default=False, verbose_name=_('Pickup available'))
    has_delivery = models.BooleanField(default=False, verbose_name=_('Delivery available'))
    has_loading_equipment = models.BooleanField(default=False, verbose_name=_('Loading equipment'))

    class Meta:
        verbose_name = _('Branch')
        verbose_name_plural = _('Branches')

    def __str__(self):
        return f'{self.city.name} - {self.address}'


class BranchImage(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='images', verbose_name=_('Branch'))
    image = models.ImageField(upload_to='uploads/branches/', verbose_name=_('Image'))
    caption = models.CharField(max_length=500, blank=True, verbose_name=_('Caption'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))

    class Meta:
        verbose_name = _('Branch image')
        verbose_name_plural = _('Branch images')
        ordering = ['order']

    def __str__(self):
        return f'{self.branch} - {self.caption or self.id}'
