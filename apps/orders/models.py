import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_tracking_number():
    return 'BK-' + uuid.uuid4().hex[:10].upper()


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        CONFIRMED = 'confirmed', _('Confirmed')
        AWAITING_DELIVERY_TO_BRANCH = 'awaiting_delivery_to_branch', _('Awaiting delivery to branch')
        AVAILABLE_IN_WAREHOUSE = 'available_in_warehouse', _('Available in warehouse')
        AWAITING_COURIER = 'awaiting_courier', _('Awaiting courier')
        PICKED_UP = 'picked_up', _('Picked up')
        IN_TRANSIT = 'in_transit', _('In transit')
        AT_WAREHOUSE = 'at_warehouse', _('At warehouse')
        OUT_FOR_DELIVERY = 'out_for_delivery', _('Out for delivery')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')

    tracking_number = models.CharField(max_length=20, unique=True, default=generate_tracking_number, verbose_name=_('Tracking number'))
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True, blank=True, related_name='orders', verbose_name=_('User'))
    sender_name = models.CharField(max_length=255, verbose_name=_('Sender name'))
    sender_phone = models.CharField(max_length=20, verbose_name=_('Sender phone'))
    sender_email = models.EmailField(blank=True, verbose_name=_('Sender email'))
    sender_address = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, related_name='sender_orders', verbose_name=_('Sender city'))
    sender_address_detail = models.CharField(max_length=500, blank=True, verbose_name=_('Sender address detail'))
    recipient_name = models.CharField(max_length=255, verbose_name=_('Recipient name'))
    recipient_phone = models.CharField(max_length=20, verbose_name=_('Recipient phone'))
    recipient_email = models.EmailField(blank=True, verbose_name=_('Recipient email'))
    recipient_address = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, related_name='recipient_orders', verbose_name=_('Recipient city'))
    recipient_address_detail = models.CharField(max_length=500, blank=True, verbose_name=_('Recipient address detail'))
    cargo_description = models.TextField(verbose_name=_('Cargo description'))
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Weight (kg)'))
    volume = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Volume (m³)'))
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Length (cm)'))
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Width (cm)'))
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Height (cm)'))
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Declared value'))
    service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, verbose_name=_('Service'))
    additional_services = models.ManyToManyField('services.AdditionalService', blank=True, verbose_name=_('Additional services'))
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.DRAFT, verbose_name=_('Status'))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Total price'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    estimated_delivery_date = models.DateField(null=True, blank=True, verbose_name=_('Estimated delivery'))
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name=_('Actual delivery'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return self.tracking_number


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name=_('Order'))
    status = models.CharField(max_length=40, choices=Order.Status.choices, verbose_name=_('Status'))
    changed_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, verbose_name=_('Changed by'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))
    comment = models.TextField(blank=True, verbose_name=_('Comment'))

    class Meta:
        verbose_name = _('Order status history')
        verbose_name_plural = _('Order status histories')
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.order.tracking_number} - {self.status} at {self.timestamp}'


class OrderDocument(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='documents', verbose_name=_('Order'))
    document_type = models.CharField(max_length=100, verbose_name=_('Document type'))
    file = models.FileField(upload_to='uploads/order_docs/', verbose_name=_('File'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded at'))

    class Meta:
        verbose_name = _('Order document')
        verbose_name_plural = _('Order documents')

    def __str__(self):
        return f'{self.order.tracking_number} - {self.document_type}'
