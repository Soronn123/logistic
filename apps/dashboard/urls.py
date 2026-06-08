from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('users/', views.DashboardUsersView.as_view(), name='users'),
    path('users/create/', views.DashboardUserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.DashboardUserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.DashboardUserDeleteView.as_view(), name='user_delete'),
    path('orders/', views.DashboardOrdersView.as_view(), name='orders'),
    path('tickets/', views.DashboardTicketsView.as_view(), name='tickets'),
    path('services/', views.DashboardServicesView.as_view(), name='services'),
    path('content/', views.DashboardContentListView.as_view(), name='content'),
    path('branches/', views.DashboardBranchesView.as_view(), name='branches'),
    path('documents/', views.DashboardDocumentsView.as_view(), name='documents'),
    path('partners/', views.DashboardPartnersView.as_view(), name='partners'),
    path('contacts/', views.DashboardContactsView.as_view(), name='contacts'),
    path('settings/', views.DashboardSettingsView.as_view(), name='settings'),
]
