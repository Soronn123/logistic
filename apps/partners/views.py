from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, TemplateView

from .models import Banner, IframeModule, PartnerApplication


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


class PartnerBannersView(ListView):
    model = Banner
    template_name = 'pages/partners/banners.html'
    context_object_name = 'banners'

    def get_queryset(self):
        return Banner.objects.filter(is_active=True)
