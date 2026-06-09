from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('reviews/', views.ReviewsView.as_view(), name='reviews'),
    path('careers/', views.VacancyListView.as_view(), name='vacancies'),
    path('careers/<slug:slug>/', views.VacancyDetailView.as_view(), name='vacancy_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('tenders/', views.TenderListView.as_view(), name='tenders'),
    path('tenders/<slug:slug>/', views.TenderDetailView.as_view(), name='tender_detail'),
    path('promotions/', views.PromotionListView.as_view(), name='promotions'),
    path('promotions/<slug:slug>/', views.PromotionDetailView.as_view(), name='promotion_detail'),
    path('directions/', views.DirectionsView.as_view(), name='directions'),
    path('tools/calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('tools/delivery-times/', views.DeliveryTimesView.as_view(), name='delivery_times'),
    path('tools/create-order/', views.CreateOrderRedirectView.as_view(), name='create_order'),
    path('tracking/', views.TrackView.as_view(), name='track'),
    path('tariffs/', views.TariffsView.as_view(), name='tariffs'),
    path('mobile-app/', views.MobileAppView.as_view(), name='mobile_app'),
    path('brand-assets/', views.BrandAssetsView.as_view(), name='brand_assets'),
    path('press/', views.PressView.as_view(), name='press'),
    path('warehouse/', views.WarehouseView.as_view(), name='warehouse'),
    path('info/<slug:page_type>/', views.InfoPageView.as_view(), name='info_page'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-use/', views.TermsOfUseView.as_view(), name='terms_of_use'),
    path('transport-terms/', views.TransportTermsView.as_view(), name='transport_terms'),
]
