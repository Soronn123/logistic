from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', '.': _('Your name')}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Your email')}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Your phone')}),
            'subject': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('Subject')}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'rows': 5, 'placeholder': _('Your message')}),
        }


class TrackingForm(forms.Form):
    tracking_number = forms.CharField(
        max_length=20,
        label=_('Tracking number'),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all',
            'placeholder': _('Enter tracking number'),
        })
    )


class CalculatorForm(forms.Form):
    from_city = forms.ModelChoiceField(
        queryset=None,
        label=_('From city'),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'})
    )
    to_city = forms.ModelChoiceField(
        queryset=None,
        label=_('To city'),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all'})
    )
    weight = forms.DecimalField(
        max_digits=10, decimal_places=2,
        label=_('Weight (kg)'),
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-baikal-500 focus:border-transparent outline-none transition-all', 'placeholder': _('e.g. 10')})
    )

    def __init__(self, *args, **kwargs):
        from apps.geo.models import City
        super().__init__(*args, **kwargs)
        self.fields['from_city'].queryset = City.objects.filter(is_active=True)
        self.fields['to_city'].queryset = City.objects.filter(is_active=True)
