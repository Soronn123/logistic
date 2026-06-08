from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from .models import Document


class DocumentListView(ListView):
    model = Document
    template_name = 'pages/documents/list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return Document.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Document.Category.choices
        return context


class CategoryDocumentView(ListView):
    model = Document
    template_name = 'pages/documents/category.html'
    context_object_name = 'documents'

    def get_queryset(self):
        self.category = self.kwargs.get('category')
        return Document.objects.filter(is_active=True, category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Document.Category.choices
        return context
