from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/settings/', views.ProfileSettingsView.as_view(), name='settings'),
    path('profile/balance/', views.BalanceView.as_view(), name='balance'),
    path('profile/balance/topup/', views.BalanceTopUpView.as_view(), name='balance_topup'),
    path('profile/balance/success/', views.BalanceSuccessView.as_view(), name='balance_success'),
    path('profile/tickets/', views.TicketListView.as_view(), name='tickets'),
    path('profile/tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('profile/tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('profile/orders/', views.OrderListView.as_view(), name='orders'),
    path('profile/orders/<slug:tracking_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('profile/documents/', views.AccountingDocumentsView.as_view(), name='accounting_docs'),
    path('profile/templates/', views.TemplatesView.as_view(), name='templates'),
    path('profile/templates/<int:pk>/edit/', views.DeliveryTemplateEditView.as_view(), name='template_edit'),
]
