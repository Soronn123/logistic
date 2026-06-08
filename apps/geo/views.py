from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from .models import Branch, City


class BranchMapView(ListView):
    model = Branch
    template_name = 'pages/geo/branches.html'
    context_object_name = 'branches'

    def get_queryset(self):
        return Branch.objects.filter(is_active=True).select_related('city').prefetch_related('images')


class CityBranchListView(DetailView):
    model = City
    template_name = 'pages/geo/city_branches.html'
    context_object_name = 'city'
    slug_field = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.filter(city=self.object, is_active=True).prefetch_related('images')
        return context
