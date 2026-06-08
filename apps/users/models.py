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
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email


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
