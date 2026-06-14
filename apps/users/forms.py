from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import CargoTemplate, CompanyApplication, ContactTemplate, CustomUser, DeliveryTemplate, Ticket, TicketMessage, Transaction


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
            'placeholder': _('Email'),
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
            'placeholder': _('Password'),
            'autocomplete': 'current-password',
        })
    )


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'phone', 'company_name', 'inn', 'is_company']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Email')}),
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Username')}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('First name')}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Last name')}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Phone')}),
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Company name')}),
            'inn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('INN')}),
            'is_company': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-baikal-600 focus:ring-baikal-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
            'placeholder': _('Password'),
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
            'placeholder': _('Confirm password'),
        })


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Email')}),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'inn', 'language', 'theme', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'inn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'language': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'theme': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'avatar': forms.FileInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['email'].initial = self.instance.email

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(_('This email is already in use.'))
        return email


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label=_('Current password'),
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Current password')}),
    )
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('New password')}),
    )
    new_password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Confirm password')}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_('Current password is incorrect.'))
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(_('Passwords do not match.'))
            if len(new_password1) < 8:
                raise forms.ValidationError(_('Password must be at least 8 characters long.'))
        return new_password2

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'priority']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Ticket subject')}),
            'priority': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
        }

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
            'rows': 5,
            'placeholder': _('Describe your issue in detail...'),
        }),
        label=_('Message'),
    )


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
                'rows': 3,
                'placeholder': _('Write your message...'),
            }),
        }


class DeliveryTemplateForm(forms.ModelForm):
    class Meta:
        model = DeliveryTemplate
        fields = ['name', 'from_city', 'to_city', 'weight', 'length', 'width', 'height', 'cargo_description', 'service', 'declared_value', 'sender_address_detail', 'recipient_address_detail', 'additional_services']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Template name')}),
            'from_city': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'to_city': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '0.1', 'min': '0.1', 'placeholder': _('Weight (kg)')}),
            'length': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '1', 'min': '0', 'placeholder': _('Length (cm)')}),
            'width': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '1', 'min': '0', 'placeholder': _('Width (cm)')}),
            'height': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '1', 'min': '0', 'placeholder': _('Height (cm)')}),
            'cargo_description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'rows': 3, 'placeholder': _('Cargo description')}),
            'service': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
            'declared_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '100', 'min': '0', 'placeholder': _('Declared value')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.geo.models import City
        from apps.services.models import Service
        self.fields['from_city'].queryset = City.objects.filter(is_active=True)
        self.fields['to_city'].queryset = City.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['from_city'].empty_label = _('Select city')
        self.fields['to_city'].empty_label = _('Select city')
        self.fields['declared_value'].required = False


class ContactTemplateForm(forms.ModelForm):
    class Meta:
        model = ContactTemplate
        fields = ['name', 'recipient_name', 'recipient_phone', 'recipient_email', 'city', 'address_detail', 'template_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Template name')}),
            'recipient_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Contact name')}),
            'recipient_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Contact phone')}),
            'recipient_email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Contact email')}),
            'address_detail': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Address detail')}),
            'template_type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.geo.models import City
        self.fields['city'].queryset = City.objects.filter(is_active=True)
        self.fields['city'].empty_label = _('Select city')
        self.fields['city'].required = False


class CompanyApplicationForm(forms.ModelForm):
    class Meta:
        model = CompanyApplication
        fields = ['company_name', 'inn']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Company name')}),
            'inn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('INN')}),
        }


class CargoTemplateForm(forms.ModelForm):
    class Meta:
        model = CargoTemplate
        fields = ['name', 'cargo_description', 'weight', 'length', 'width', 'height', 'declared_value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Template name')}),
            'cargo_description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'rows': 3, 'placeholder': _('Cargo description')}),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '0.1', 'min': '0.1', 'placeholder': _('Weight (kg)')}),
            'length': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '1', 'min': '0', 'placeholder': _('Length (cm)')}),
            'width': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '1', 'min': '0', 'placeholder': _('Width (cm)')}),
            'height': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '1', 'min': '0', 'placeholder': _('Height (cm)')}),
            'declared_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'step': '100', 'min': '0', 'placeholder': _('Declared value (₽)')}),
        }
