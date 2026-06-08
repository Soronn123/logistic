from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('', include('apps.users.urls', namespace='users')),
    path('services/', include('apps.services.urls', namespace='services')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('geo/', include('apps.geo.urls', namespace='geo')),
    path('partners/', include('apps.partners.urls', namespace='partners')),
    path('documents/', include('apps.documents.urls', namespace='documents')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
