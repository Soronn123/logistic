from django.conf import settings


def site_settings(request):
    return {
        'SITE_NAME': 'Baikal-Service',
        'SITE_DESCRIPTION': 'Logistics and cargo transportation across Russia and CIS',
        'theme': getattr(request, 'theme', 'light'),
        'DEBUG': settings.DEBUG,
    }
