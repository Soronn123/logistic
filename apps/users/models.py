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
    """Single contact entry - can be used for either sender or recipient."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='contact_templates', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Template name'))
    contact_name = models.CharField(max_length=255, verbose_name=_('Contact name'))
    contact_phone = models.CharField(max_length=20, verbose_name=_('Contact phone'))
    contact_email = models.EmailField(blank=True, verbose_name=_('Contact email'))
    city = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('City'))
    address_detail = models.CharField(max_length=500, blank=True, verbose_name=_('Address detail'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Contact template')
        verbose_name_plural = _('Contact templates')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.contact_name}'


class DeliveryTemplate(models.Model):
    """Service + additional services template."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='delivery_templates', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Template name'))
    service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Service'))
    additional_services = models.ManyToManyField('services.AdditionalService', blank=True, verbose_name=_('Additional services'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Delivery template')
        verbose_name_plural = _('Delivery templates')
        db_table = 'users_deliverytemplate'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.service}'


MasterTemplate = DeliveryTemplate  # Alias for backward compatibility


class CargoTemplate(models.Model):
    """Deprecated - kept for migration compatibility. Use MasterTemplate instead."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='cargo_templates_deprecated', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Template name'))
    cargo_description = models.TextField(blank=True, verbose_name=_('Cargo description'))
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Weight (kg)'))
    length = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, verbose_name=_('Length (cm)'))
    width = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, verbose_name=_('Width (cm)'))
    height = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, verbose_name=_('Height (cm)'))
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Declared value'))
    is_fragile = models.BooleanField(default=False, verbose_name=_('Fragile cargo'))
    is_dangerous = models.BooleanField(default=False, verbose_name=_('Dangerous goods'))
    is_temperature_sensitive = models.BooleanField(default=False, verbose_name=_('Temperature-sensitive cargo'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Cargo template (deprecated)')
        verbose_name_plural = _('Cargo templates (deprecated)')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} (deprecated)'



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


class CompanyApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        REVIEWING = 'reviewing', _('Under review')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='company_applications', verbose_name=_('User'))
    company_name = models.CharField(max_length=255, verbose_name=_('Company name'))
    inn = models.CharField(max_length=12, verbose_name=_('INN'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('Status'))
    admin_comment = models.TextField(blank=True, verbose_name=_('Admin comment'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Company application')
        verbose_name_plural = _('Company applications')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company_name} ({self.user.email}) - {self.get_status_display()}'


class ManagerDirectoryPermission(models.Model):
    class Directory(models.TextChoices):
        CITIES = 'cities', _('Cities')
        BRANCHES = 'branches', _('Branches')
        SERVICES = 'services', _('Services')
        SERVICE_CATEGORIES = 'service_categories', _('Service categories')
        ADDITIONAL_SERVICES = 'additional_services', _('Additional services')
        TARIFFS = 'tariffs', _('Tariffs')
        DOCUMENTS = 'documents', _('Documents')
        FAQ = 'faq', _('FAQ')
        NEWS = 'news', _('News')
        VACANCIES = 'vacancies', _('Vacancies')
        PROMOTIONS = 'promotions', _('Promotions')
        BANNERS = 'banners', _('Banners')
        REVIEWS = 'reviews', _('Reviews')
        CONTENT_PAGES = 'content_pages', _('Content pages')
        ORDERS = 'orders', _('Orders')
        TICKETS = 'tickets', _('Tickets')
        PARTNER_APPLICATIONS = 'partner_applications', _('Partner applications')

    manager = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'role': 'manager'},
        related_name='directory_permissions',
        verbose_name=_('Manager')
    )
    directory = models.CharField(
        max_length=50, choices=Directory.choices,
        verbose_name=_('Directory')
    )
    can_access = models.BooleanField(default=False, verbose_name=_('Can access'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Manager directory permission')
        verbose_name_plural = _('Manager directory permissions')
        unique_together = ['manager', 'directory']
        ordering = ['manager', 'directory']

    def __str__(self):
        return f'{self.manager.email} - {self.get_directory_display()}: {"Allowed" if self.can_access else "Denied"}'
