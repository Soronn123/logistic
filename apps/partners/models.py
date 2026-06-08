from django.db import models
from django.utils.translation import gettext_lazy as _


class PartnerApplication(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', _('New')
        REVIEWING = 'reviewing', _('Reviewing')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    company_name = models.CharField(max_length=255, verbose_name=_('Company name'))
    contact_person = models.CharField(max_length=255, verbose_name=_('Contact person'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Partner application')
        verbose_name_plural = _('Partner applications')
        ordering = ['-created_at']

    def __str__(self):
        return self.company_name


class Banner(models.Model):
    class Placement(models.TextChoices):
        HEADER = 'header', _('Header')
        SIDEBAR = 'sidebar', _('Sidebar')
        FOOTER = 'footer', _('Footer')

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    image = models.ImageField(upload_to='banners/', verbose_name=_('Image'))
    link = models.URLField(blank=True, verbose_name=_('Link'))
    placement = models.CharField(max_length=20, choices=Placement.choices, default=Placement.HEADER, verbose_name=_('Placement'))
    start_date = models.DateTimeField(verbose_name=_('Start date'))
    end_date = models.DateTimeField(verbose_name=_('End date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    clicks_count = models.IntegerField(default=0, verbose_name=_('Clicks count'))

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')

    def __str__(self):
        return self.title


class IframeModule(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    embed_code = models.TextField(verbose_name=_('Embed code'))
    documentation = models.TextField(blank=True, verbose_name=_('Documentation'))

    class Meta:
        verbose_name = _('iFrame module')
        verbose_name_plural = _('iFrame modules')

    def __str__(self):
        return self.name
