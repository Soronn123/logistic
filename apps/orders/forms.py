import re

from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from .models import Order

from apps.geo.services import validate_address


PHONE_PATTERN = re.compile(r'^(\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'sender_name', 'sender_phone', 'sender_email', 'sender_address', 'sender_address_detail',
            'recipient_name', 'recipient_phone', 'recipient_email', 'recipient_address', 'recipient_address_detail',
            'cargo_description', 'weight', 'volume', 'length', 'width', 'height',
            'declared_value', 'service', 'additional_services',
            'is_fragile', 'is_dangerous', 'is_temperature_sensitive',
        ]
        widgets = {
            'sender_name': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': _('Full name or company name'),
            }),
            'sender_phone': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': '+7 (999) 123-45-67',
            }),
            'sender_email': forms.EmailInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': 'email@example.com',
            }),
            'sender_address': forms.Select(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
            }),
            'sender_address_detail': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': _('Street, building, apartment'),
            }),
            'recipient_name': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': _('Full name or company name'),
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': '+7 (999) 123-45-67',
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': 'email@example.com',
            }),
            'recipient_address': forms.Select(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
            }),
            'recipient_address_detail': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'placeholder': _('Street, building, apartment'),
            }),
            'cargo_description': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'rows': 3,
                'placeholder': _('Describe the cargo, contents, and special handling requirements...'),
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'step': '0.1', 'min': '0.1',
                'placeholder': '0',
            }),
            'length': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'step': '1', 'min': '0',
                'placeholder': '0',
            }),
            'width': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'step': '1', 'min': '0',
                'placeholder': '0',
            }),
            'height': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'step': '1', 'min': '0',
                'placeholder': '0',
            }),
            'declared_value': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500 transition-colors',
                'step': '100', 'min': '0',
                'placeholder': _('Cargo value for insurance'),
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from apps.geo.models import City
        from apps.services.models import AdditionalService, Service
        self.fields['sender_address'].queryset = City.objects.filter(is_active=True)
        self.fields['recipient_address'].queryset = City.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True).distinct()
        self.fields['additional_services'].queryset = AdditionalService.objects.all().distinct()
        self.fields['sender_address'].empty_label = _('Select city')
        self.fields['recipient_address'].empty_label = _('Select city')
        self.fields['volume'].required = False
        self.fields['length'].required = False
        self.fields['width'].required = False
        self.fields['height'].required = False
        self.fields['declared_value'].required = False
        self.fields['sender_address_detail'].required = False
        self.fields['recipient_address_detail'].required = False
        self.fields['sender_email'].required = False
        self.fields['recipient_email'].required = False

        if user:
            self.fields['sender_name'].initial = (
                f'{user.first_name} {user.last_name}'.strip()
                or (user.company_name if user.is_company else '')
                or ''
            )
            self.fields['sender_phone'].initial = user.phone or ''
            self.fields['sender_email'].initial = user.email or ''

    def clean(self):
        cleaned_data = super().clean()
        sender_name = cleaned_data.get('sender_name', '').strip()
        sender_phone = cleaned_data.get('sender_phone', '').strip()
        sender_address = cleaned_data.get('sender_address')
        recipient_name = cleaned_data.get('recipient_name', '').strip()
        recipient_phone = cleaned_data.get('recipient_phone', '').strip()
        recipient_address = cleaned_data.get('recipient_address')
        additional_services = cleaned_data.get('additional_services')

        if not sender_name:
            self.add_error('sender_name', _('Sender name is required'))
        if not sender_phone:
            self.add_error('sender_phone', _('Sender phone is required'))
        if not sender_address:
            self.add_error('sender_address', _('Sender city is required'))
        if not recipient_name:
            self.add_error('recipient_name', _('Recipient name is required'))
        if not recipient_phone:
            self.add_error('recipient_phone', _('Recipient phone is required'))
        if not recipient_address:
            self.add_error('recipient_address', _('Recipient city is required'))

        if additional_services and recipient_address:
            from apps.geo.models import Branch
            is_branch_delivery = Branch.objects.filter(
                city=recipient_address, is_active=True
            ).exists()
            if is_branch_delivery:
                door_services = additional_services.filter(is_door_service=True)
                if door_services.exists():
                    self.add_error(
                        'additional_services',
                        _('Door-to-door services are not available for pickup point delivery')
                    )

        phone_pattern = PHONE_PATTERN
        if sender_phone and not phone_pattern.match(sender_phone):
            self.add_error('sender_phone', _('Invalid phone format. Use +7 (999) 123-45-67'))
        if recipient_phone and not phone_pattern.match(recipient_phone):
            self.add_error('recipient_phone', _('Invalid phone format. Use +7 (999) 123-45-67'))

        sender_email = cleaned_data.get('sender_email', '').strip()
        recipient_email = cleaned_data.get('recipient_email', '').strip()
        if sender_email:
            try:
                validate_email(sender_email)
            except forms.ValidationError:
                self.add_error('sender_email', _('Invalid email format'))
        if recipient_email:
            try:
                validate_email(recipient_email)
            except forms.ValidationError:
                self.add_error('recipient_email', _('Invalid email format'))

        sender_address_detail = cleaned_data.get('sender_address_detail', '').strip()
        recipient_address_detail = cleaned_data.get('recipient_address_detail', '').strip()
        if sender_address_detail:
            valid, error_msg = validate_address(sender_address_detail)
            if not valid:
                self.add_error('sender_address_detail', error_msg)
        if recipient_address_detail:
            valid, error_msg = validate_address(recipient_address_detail)
            if not valid:
                self.add_error('recipient_address_detail', error_msg)

        return cleaned_data
