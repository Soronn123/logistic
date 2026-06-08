from django.db import models
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    class Category(models.TextChoices):
        CONTRACTS = 'contracts', _('Contracts')
        SHIPPING_DOCS = 'shipping_docs', _('Shipping documents')
        RECEIPT_DOCS = 'receipt_docs', _('Receipt documents')
        POWER_OF_ATTORNEY = 'power_of_attorney', _('Power of attorney')
        CHARTER = 'charter', _('Charter')
        CLAIMS = 'claims', _('Claims')
        REFUNDS = 'refunds', _('Refunds')
        TUE_REPLACEMENT = 'tue_replacement', _('TUE replacement')

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    title_en = models.CharField(max_length=255, blank=True, verbose_name=_('Title (EN)'))
    category = models.CharField(max_length=30, choices=Category.choices, verbose_name=_('Category'))
    file = models.FileField(upload_to='documents/', verbose_name=_('File'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded at'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['category', 'title']

    def __str__(self):
        return self.title


class AccountingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        FULFILLED = 'fulfilled', _('Fulfilled')
        REJECTED = 'rejected', _('Rejected')

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='accounting_requests', verbose_name=_('User'))
    document_type = models.CharField(max_length=100, verbose_name=_('Document type'))
    period_start = models.DateField(verbose_name=_('Period start'))
    period_end = models.DateField(verbose_name=_('Period end'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    fulfilled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Fulfilled at'))

    class Meta:
        verbose_name = _('Accounting request')
        verbose_name_plural = _('Accounting requests')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.document_type} ({self.period_start} to {self.period_end})'
