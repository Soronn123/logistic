from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, TemplateView

from .models import Banner, IframeModule, Partner, PartnerApplication


class PartnerOverviewView(TemplateView):
    template_name = 'pages/partners/overview.html'


class PartnerApplyView(CreateView):
    model = PartnerApplication
    fields = ['company_name', 'contact_person', 'email', 'phone', 'website']
    template_name = 'pages/partners/apply.html'
    success_url = reverse_lazy('partners:apply')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = self.request.GET.get('success', False)
        return context


class IframeModulesView(ListView):
    model = IframeModule
    template_name = 'pages/partners/iframe.html'
    context_object_name = 'modules'


class PartnerListView(ListView):
    model = Partner
    template_name = 'pages/partners/partner_list.html'
    context_object_name = 'partners'
    paginate_by = 12

    def get_queryset(self):
        return Partner.objects.filter(is_active=True)


def partner_cards_partial(request):
    page = int(request.GET.get('page', 1))
    per_page = 6
    start = (page - 1) * per_page
    end = start + per_page
    partners = Partner.objects.filter(is_active=True)[start:end + 1]
    has_next = len(partners) > per_page
    partners = list(partners[:per_page])
    return render(request, 'partials/_partner_cards.html', {
        'partners': partners,
        'page': page,
        'has_next': has_next,
    })


class PartnerBannersView(ListView):
    model = Banner
    template_name = 'pages/partners/banners.html'
    context_object_name = 'banners'

    def get_queryset(self):
        return Banner.objects.filter(is_active=True)
