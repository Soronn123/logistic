from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Role(models.TextChoices):
        CLIENT = 'client', _('Client')
        MANAGER = 'manager', _('Manager')
        ADMIN = 'admin', _('Admin')

    email = models.EmailField(unique=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Balance'))
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, verbose_name=_('Role'))
    language = models.CharField(max_length=5, choices=[('ru', 'Русский'), ('en', 'English')], default='ru', verbose_name=_('Language'))
    theme = models.CharField(max_length=10, choices=[('light', _('Light')), ('dark', _('Dark'))], default='light', verbose_name=_('Theme'))
    company_name = models.CharField(max_length=255, blank=True, verbose_name=_('Company name'))
    inn = models.CharField(max_length=12, blank=True, verbose_name=_('INN'))
    is_company = models.BooleanField(default=False, verbose_name=_('Legal entity'))
    avatar = models.ImageField(upload_to='uploads/avatars/', blank=True, null=True, verbose_name=_('Avatar'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email


class ContactTemplate(models.Model):
    class TemplateType(models.TextChoices):
        SENDER = 'sender', _('Sender')
        RECIPIENT = 'recipient', _('Recipient')

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='contact_templates', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Template name'))
    template_type = models.CharField(max_length=20, choices=TemplateType.choices, default=TemplateType.RECIPIENT, verbose_name=_('Template type'))
    recipient_name = models.CharField(max_length=255, verbose_name=_('Contact name'))
    recipient_phone = models.CharField(max_length=20, verbose_name=_('Contact phone'))
    recipient_email = models.EmailField(blank=True, verbose_name=_('Contact email'))
    city = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, verbose_name=_('City'))
    address_detail = models.CharField(max_length=500, blank=True, verbose_name=_('Address detail'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Contact template')
        verbose_name_plural = _('Contact templates')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.recipient_name}'


class DeliveryTemplate(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='delivery_templates', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Template name'))
    from_city = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, related_name='delivery_template_from', verbose_name=_('From city'))
    to_city = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, related_name='delivery_template_to', verbose_name=_('To city'))
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Weight (kg)'))
    cargo_description = models.TextField(blank=True, verbose_name=_('Cargo description'))
    service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, verbose_name=_('Service'))
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Declared value'))
    sender_address_detail = models.CharField(max_length=500, blank=True, verbose_name=_('Sender address detail'))
    recipient_address_detail = models.CharField(max_length=500, blank=True, verbose_name=_('Recipient address detail'))
    additional_services = models.ManyToManyField('services.AdditionalService', blank=True, verbose_name=_('Additional services'))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Total price'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Delivery template')
        verbose_name_plural = _('Delivery templates')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.from_city} → {self.to_city}'


class CargoTemplate(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='cargo_templates', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Template name'))
    cargo_description = models.TextField(blank=True, verbose_name=_('Cargo description'))
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Weight (kg)'))
    length = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, verbose_name=_('Length (cm)'))
    width = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, verbose_name=_('Width (cm)'))
    height = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, verbose_name=_('Height (cm)'))
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Declared value'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Cargo template')
        verbose_name_plural = _('Cargo templates')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.cargo_description[:30]}'


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In progress')
        CLOSED = 'closed', _('Closed')

    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')

    subject = models.CharField(max_length=500, verbose_name=_('Subject'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name=_('Status'))
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM, verbose_name=_('Priority'))
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets', verbose_name=_('Created by'))
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name=_('Assigned to'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.id} {self.subject}'


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name=_('Ticket'))
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('Sender'))
    message = models.TextField(verbose_name=_('Message'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    is_internal_note = models.BooleanField(default=False, verbose_name=_('Internal note'))

    class Meta:
        verbose_name = _('Ticket message')
        verbose_name_plural = _('Ticket messages')
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.email}: {self.message[:50]}'


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'deposit', _('Deposit')
        WITHDRAWAL = 'withdrawal', _('Withdrawal')
        REFUND = 'refund', _('Refund')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('User'))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Amount'))
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, verbose_name=_('Transaction type'))
    description = models.CharField(max_length=500, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Balance after'))

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_type} {self.amount} - {self.user.email}'
