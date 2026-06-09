from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, RedirectView

from .forms import CalculatorForm, ContactForm, TrackingForm
from .models import ContactMessage, ContentPage, FAQ, NewsItem, Promotion, Review, Vacancy, Tender


class HomeView(TemplateView):
    template_name = 'pages/core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_items'] = NewsItem.objects.filter(is_published=True, is_pinned=True)[:3]
        context['reviews'] = Review.objects.filter(is_approved=True)[:5]
        context['tracking_form'] = TrackingForm()
        context['calculator_form'] = CalculatorForm()
        context['promotions'] = Promotion.objects.filter(is_active=True)[:3]
        from apps.geo.models import City, Branch
        from apps.services.models import Service
        context['cities'] = City.objects.filter(is_active=True)[:50]
        context['services'] = Service.objects.filter(is_active=True)[:10]
        context['branches'] = Branch.objects.filter(is_active=True).select_related('city')[:100]
        return context


class AboutView(TemplateView):
    template_name = 'pages/core/about.html'


class NewsListView(ListView):
    model = NewsItem
    template_name = 'pages/core/news_list.html'
    context_object_name = 'news_items'
    paginate_by = 9

    def get_queryset(self):
        return NewsItem.objects.filter(is_published=True)


class NewsDetailView(DetailView):
    model = NewsItem
    template_name = 'pages/core/news_detail.html'
    context_object_name = 'news_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_news'] = NewsItem.objects.filter(is_published=True).exclude(id=self.object.id)[:3]
        return context


class ReviewsView(ListView):
    model = Review
    template_name = 'pages/core/reviews.html'
    context_object_name = 'reviews'
    paginate_by = 12

    def get_queryset(self):
        qs = Review.objects.filter(is_approved=True)
        rating = self.request.GET.get('rating')
        if rating:
            qs = qs.filter(rating=rating)
        return qs


class VacancyListView(ListView):
    model = Vacancy
    template_name = 'pages/core/vacancies.html'
    context_object_name = 'vacancies'

    def get_queryset(self):
        qs = Vacancy.objects.filter(is_active=True)
        dept = self.request.GET.get('department')
        city = self.request.GET.get('city')
        if dept:
            qs = qs.filter(department=dept)
        if city:
            qs = qs.filter(city_id=city)
        return qs


class VacancyDetailView(DetailView):
    model = Vacancy
    template_name = 'pages/core/vacancy_detail.html'
    context_object_name = 'vacancy'


class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'pages/core/contact.html'
    success_url = reverse_lazy('core:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = self.request.GET.get('success', False)
        return context


class FAQView(ListView):
    model = FAQ
    template_name = 'pages/core/faq.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        return FAQ.objects.filter(is_published=True)


class TenderListView(ListView):
    model = Tender
    template_name = 'pages/core/tenders.html'
    context_object_name = 'tenders'

    def get_queryset(self):
        return Tender.objects.filter(is_active=True)


class TenderDetailView(DetailView):
    model = Tender
    template_name = 'pages/core/tender_detail.html'
    context_object_name = 'tender'


class PromotionListView(ListView):
    model = Promotion
    template_name = 'pages/core/promotions.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True)


class PromotionDetailView(DetailView):
    model = Promotion
    template_name = 'pages/core/promotion_detail.html'
    context_object_name = 'promotion'


class DirectionsView(TemplateView):
    template_name = 'pages/core/directions.html'


class CalculatorView(FormView):
    form_class = CalculatorForm
    template_name = 'pages/core/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.geo.models import City
        from apps.services.models import Service
        context['cities'] = City.objects.filter(is_active=True)
        context['services'] = Service.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        from apps.services.models import Tariff
        weight = form.cleaned_data['weight']
        from_city = form.cleaned_data['from_city']
        to_city = form.cleaned_data['to_city']
        tariffs = Tariff.objects.filter(
            min_weight__lte=weight
        ).filter(
            max_weight__gte=weight
        ) | Tariff.objects.filter(
            min_weight__lte=weight, max_weight__isnull=True
        )
        context = {
            'estimates': tariffs,
            'weight': weight,
            'from_city_name': str(from_city),
            'to_city_name': str(to_city),
        }
        if self.request.headers.get('HX-Request'):
            from django.shortcuts import render
            return render(self.request, 'partials/_calculator_results.html', context)
        return self.render_to_response(self.get_context_data(
            form=form, estimates=tariffs
        ))


class TrackView(FormView):
    form_class = TrackingForm
    template_name = 'pages/core/track.html'

    def form_valid(self, form):
        from django.shortcuts import render
        from apps.orders.models import Order
        tn = form.cleaned_data['tracking_number']
        try:
            order = Order.objects.get(tracking_number=tn)
            context = {'order': order}
        except Order.DoesNotExist:
            context = {'error': _('Order not found')}
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'partials/_tracking_results.html', context)
        return self.render_to_response(self.get_context_data(**context, form=form))


class DeliveryTimesView(TemplateView):
    template_name = 'pages/core/delivery_times.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.geo.models import City
        from apps.services.models import Tariff
        context['cities'] = City.objects.filter(is_active=True)
        from_city = self.request.GET.get('from')
        to_city = self.request.GET.get('to')
        delivery_times = []
        if from_city and to_city:
            try:
                from_city_obj = City.objects.get(id=from_city)
                to_city_obj = City.objects.get(id=to_city)
            except (City.DoesNotExist, ValueError):
                from_city_obj = None
                to_city_obj = None
            if from_city_obj and to_city_obj:
                tariffs = Tariff.objects.all()
                for tariff in tariffs:
                    delivery_times.append({
                        'from_city': from_city_obj,
                        'to_city': to_city_obj,
                        'min_days': tariff.delivery_days_min or 1,
                        'max_days': tariff.delivery_days_max or 14,
                        'service_type': tariff.name,
                    })
                if not delivery_times:
                    delivery_times.append({
                        'from_city': from_city_obj,
                        'to_city': to_city_obj,
                        'min_days': 1,
                        'max_days': 7,
                        'service_type': 'Standard',
                    })
        context['delivery_times'] = delivery_times
        return context


class CreateOrderRedirectView(RedirectView):
    pattern_name = 'orders:create'


class TariffsView(TemplateView):
    template_name = 'pages/core/tariffs.html'


class MobileAppView(TemplateView):
    template_name = 'pages/core/mobile_app.html'


class BrandAssetsView(TemplateView):
    template_name = 'pages/core/brand_assets.html'


class InfoPageView(TemplateView):
    template_name = 'pages/core/info_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_type = self.kwargs.get('page_type', '')
        context['page'] = get_object_or_404(ContentPage, slug=page_type, is_published=True)
        return context


class PressView(TemplateView):
    template_name = 'pages/core/press.html'


class WarehouseView(TemplateView):
    template_name = 'pages/core/warehouse.html'
