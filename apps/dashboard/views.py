from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView, DeleteView, CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django import forms

from apps.services.models import Service, ServiceCategory, AdditionalService, Tariff
from apps.geo.models import Branch, City
from apps.partners.models import PartnerApplication, Banner
from apps.core.models import ContentPage, NewsItem, Vacancy, FAQ, Review, Tender

User = get_user_model()

ICON_CHOICES = [
    'fa-truck', 'fa-box', 'fa-plane', 'fa-ship', 'fa-train',
    'fa-warehouse', 'fa-store', 'fa-laptop', 'fa-archive',
    'fa-pallet', 'fa-envelope', 'fa-clock', 'fa-shield',
    'fa-truck-fast', 'fa-people-carry-box', 'fa-handshake',
]


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role in ['admin', 'manager']

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('dashboard:login')
        return redirect('core:home')

    @property
    def is_admin(self):
        return self.request.user.role == 'admin'

    @property
    def is_manager(self):
        return self.request.user.role == 'manager'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.role in ['admin', 'manager']):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(StaffRequiredMixin):
    def test_func(self):
        return self.request.user.role == 'manager' or self.is_admin


class DashboardLoginView(TemplateView):
    template_name = 'pages/dashboard/login.html'

    def post(self, request, *args, **kwargs):
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None and (user.is_staff or user.role in ['admin', 'manager']):
            login(request, user)
            return redirect('dashboard:home')
        return self.render_to_response(self.get_context_data(form_errors=True))


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        today = timezone.now().date()
        try:
            from apps.orders.models import Order
            context['today_orders'] = Order.objects.filter(created_at__date=today).count()
            context['active_shipments'] = Order.objects.filter(
                status__in=['in_transit', 'picked_up', 'at_warehouse']
            ).count()
            context['recent_orders'] = Order.objects.all()[:5]
        except ImportError:
            context['today_orders'] = 0
            context['active_shipments'] = 0
            context['recent_orders'] = []
        try:
            from apps.users.models import Ticket
            context['open_tickets'] = Ticket.objects.filter(status__in=['open', 'in_progress']).count()
        except ImportError:
            context['open_tickets'] = 0
        context['total_users'] = User.objects.count()
        return context


class DashboardUsersView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()[:50]
        return context


class DashboardUserForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'is_active', 'balance',
                  'company_name', 'inn', 'is_company', 'language', 'theme']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'balance': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'company_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'inn': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'role': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'language': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'theme': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm focus:ring-2 focus:ring-baikal-500 focus:border-baikal-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 dark:border-gray-600 text-baikal-600 focus:ring-baikal-500'}),
            'is_company': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 dark:border-gray-600 text-baikal-600 focus:ring-baikal-500'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class DashboardUserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = DashboardUserForm
    template_name = 'pages/dashboard/user_form.html'
    success_url = reverse_lazy('dashboard:users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('User created successfully.'))
        return super().form_valid(form)


class DashboardUserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = DashboardUserForm
    template_name = 'pages/dashboard/user_form.html'
    success_url = reverse_lazy('dashboard:users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('User updated successfully.'))
        return super().form_valid(form)


class DashboardUserDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'pages/dashboard/user_confirm_delete.html'
    success_url = reverse_lazy('dashboard:users')

    def test_func(self):
        return self.is_admin

    def form_valid(self, form):
        messages.success(self.request, _('User deleted successfully.'))
        return super().form_valid(form)


class DashboardOrdersView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.orders.models import Order
            context['orders'] = Order.objects.all()[:50]
        except ImportError:
            context['orders'] = []
        return context


class DashboardTicketsView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/tickets.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.users.models import Ticket
            tickets = Ticket.objects.all()[:50]
            context['tickets'] = tickets
            context['open_count'] = Ticket.objects.filter(status='open').count()
            context['in_progress_count'] = Ticket.objects.filter(status='in_progress').count()
            context['closed_count'] = Ticket.objects.filter(status='closed').count()
        except ImportError:
            context['tickets'] = []
            context['open_count'] = 0
            context['in_progress_count'] = 0
            context['closed_count'] = 0
        return context


class DashboardServicesView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.all()
        context['services'] = Service.objects.all()[:50]
        context['additional_services'] = AdditionalService.objects.all()
        context['tariffs'] = Tariff.objects.all()
        context['icon_choices'] = ICON_CHOICES
        context['cities'] = City.objects.filter(is_active=True)
        return context


class DashboardContentListView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.core.models import ContentPage, NewsItem, Vacancy, FAQ, Review, Tender
            context['content_pages'] = ContentPage.objects.all()[:50]
            context['news_items'] = NewsItem.objects.all()[:20]
            context['vacancies'] = Vacancy.objects.all()[:20]
            context['faqs'] = FAQ.objects.all()[:50]
            context['reviews'] = Review.objects.all()[:50]
            context['tenders'] = Tender.objects.all()[:20]
        except ImportError:
            context['pages'] = []
            context['news'] = []
            context['vacancies'] = []
            context['faqs'] = []
            context['reviews'] = []
            context['tenders'] = []
        return context


class DashboardBranchesView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/branches.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.geo.models import Branch, City
            context['branches'] = Branch.objects.all()[:50]
            context['cities'] = City.objects.all()
        except ImportError:
            context['branches'] = []
            context['cities'] = []
        return context


class DashboardDocumentsView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/documents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.documents.models import Document, AccountingRequest
            context['documents'] = Document.objects.all()[:50]
            context['accounting_requests'] = AccountingRequest.objects.all()[:20]
        except ImportError:
            context['documents'] = []
            context['accounting_requests'] = []
        return context


class DashboardPartnersView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/partners.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.partners.models import PartnerApplication, Banner
            context['applications'] = PartnerApplication.objects.all()[:50]
            context['banners'] = Banner.objects.all()[:50]
        except ImportError:
            context['applications'] = []
            context['banners'] = []
        return context


class DashboardContactsView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.core.models import ContactMessage
            context['messages'] = ContactMessage.objects.all()[:50]
            context['total_messages'] = ContactMessage.objects.count()
            context['unread_count'] = ContactMessage.objects.filter(is_read=False).count()
        except ImportError:
            context['messages'] = []
            context['total_messages'] = 0
            context['unread_count'] = 0
        return context


class DashboardSettingsView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/settings.html'

    def post(self, request, *args, **kwargs):
        messages.success(request, _('Settings saved successfully.'))
        return redirect('dashboard:settings')


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'name', 'name_en', 'slug', 'description', 'description_en',
                  'short_description', 'short_description_en', 'icon', 'base_price',
                  'price_unit', 'is_active', 'sort_order']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'name_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'description_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'short_description': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'short_description_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'icon': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'base_price': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'price_unit': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'sort_order': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = forms.Select(choices=[(c, c) for c in ICON_CHOICES], attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'})


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['city', 'branch_type', 'address', 'address_en', 'phone', 'email',
                  'working_hours', 'latitude', 'longitude', 'is_active',
                  'has_pickup', 'has_delivery', 'has_loading_equipment']
        widgets = {
            'city': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'branch_type': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'address': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'address_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'phone': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'working_hours': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm font-mono text-xs', 'rows': 4, 'placeholder': '{"mon-fri": "09:00-20:00", "sat": "10:00-18:00", "sun": "closed"}'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': 'any'}),
        }


class DashboardServiceCreateView(StaffRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'pages/dashboard/service_form.html'
    success_url = reverse_lazy('dashboard:services')

    def form_valid(self, form):
        messages.success(self.request, _('Service created successfully.'))
        return super().form_valid(form)


class DashboardServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'pages/dashboard/service_form.html'
    success_url = reverse_lazy('dashboard:services')

    def form_valid(self, form):
        messages.success(self.request, _('Service updated successfully.'))
        return super().form_valid(form)


class DashboardServiceDeleteView(StaffRequiredMixin, DeleteView):
    model = Service
    template_name = 'pages/dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('dashboard:services')

    def test_func(self):
        return self.is_admin

    def form_valid(self, form):
        messages.success(self.request, _('Service deleted successfully.'))
        return super().form_valid(form)


class DashboardBranchCreateView(StaffRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'pages/dashboard/branch_form.html'
    success_url = reverse_lazy('dashboard:branches')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Branch created successfully.'))
        return super().form_valid(form)


class DashboardBranchUpdateView(StaffRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'pages/dashboard/branch_form.html'
    success_url = reverse_lazy('dashboard:branches')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Branch updated successfully.'))
        return super().form_valid(form)


class DashboardBranchDeleteView(StaffRequiredMixin, DeleteView):
    model = Branch
    template_name = 'pages/dashboard/branch_confirm_delete.html'
    success_url = reverse_lazy('dashboard:branches')

    def form_valid(self, form):
        messages.success(self.request, _('Branch deleted successfully.'))
        return super().form_valid(form)


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'name_en', 'slug', 'icon', 'description', 'description_en', 'order', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'name_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'description_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'parent': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = forms.Select(choices=[(c, c) for c in ICON_CHOICES], attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'})
        self.fields['parent'].queryset = ServiceCategory.objects.all()
        self.fields['parent'].required = False


class DashboardServiceCategoryCreateView(StaffRequiredMixin, CreateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = 'pages/dashboard/category_form.html'
    success_url = reverse_lazy('dashboard:services')

    def form_valid(self, form):
        messages.success(self.request, _('Category created successfully.'))
        return super().form_valid(form)


class DashboardServiceCategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = 'pages/dashboard/category_form.html'
    success_url = reverse_lazy('dashboard:services')

    def form_valid(self, form):
        messages.success(self.request, _('Category updated successfully.'))
        return super().form_valid(form)


class DashboardServiceCategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = ServiceCategory
    template_name = 'pages/dashboard/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:services')

    def test_func(self):
        return self.is_admin

    def form_valid(self, form):
        messages.success(self.request, _('Category deleted successfully.'))
        return super().form_valid(form)


class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'name_en', 'description', 'description_en', 'min_weight', 'max_weight', 'price_per_kg', 'delivery_days_min', 'delivery_days_max']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'name_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'description_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'min_weight': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'max_weight': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'price_per_kg': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'delivery_days_min': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'delivery_days_max': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }


class DashboardTariffCreateView(StaffRequiredMixin, CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'pages/dashboard/tariff_form.html'
    success_url = reverse_lazy('dashboard:services')

    def form_valid(self, form):
        messages.success(self.request, _('Tariff created successfully.'))
        return super().form_valid(form)


class DashboardTariffUpdateView(StaffRequiredMixin, UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'pages/dashboard/tariff_form.html'
    success_url = reverse_lazy('dashboard:services')

    def form_valid(self, form):
        messages.success(self.request, _('Tariff updated successfully.'))
        return super().form_valid(form)


class DashboardTariffDeleteView(StaffRequiredMixin, DeleteView):
    model = Tariff
    template_name = 'pages/dashboard/tariff_confirm_delete.html'
    success_url = reverse_lazy('dashboard:services')

    def test_func(self):
        return self.is_admin

    def form_valid(self, form):
        messages.success(self.request, _('Tariff deleted successfully.'))
        return super().form_valid(form)


class PartnerApplicationForm(forms.ModelForm):
    class Meta:
        model = PartnerApplication
        fields = ['company_name', 'contact_person', 'email', 'phone', 'website', 'status']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'phone': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'website': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'status': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }


class DashboardPartnerApplicationUpdateView(StaffRequiredMixin, UpdateView):
    model = PartnerApplication
    form_class = PartnerApplicationForm
    template_name = 'pages/dashboard/partner_application_form.html'
    success_url = reverse_lazy('dashboard:partners')

    def form_valid(self, form):
        messages.success(self.request, _('Partner application updated successfully.'))
        return super().form_valid(form)


class DashboardPartnerApplicationDeleteView(StaffRequiredMixin, DeleteView):
    model = PartnerApplication
    template_name = 'pages/dashboard/partner_application_confirm_delete.html'
    success_url = reverse_lazy('dashboard:partners')

    def form_valid(self, form):
        messages.success(self.request, _('Partner application deleted successfully.'))
        return super().form_valid(form)


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'link', 'placement', 'start_date', 'end_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'image': forms.FileInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'link': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'placement': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'type': 'datetime-local'}),
        }


class DashboardBannerCreateView(StaffRequiredMixin, CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'pages/dashboard/banner_form.html'
    success_url = reverse_lazy('dashboard:partners')

    def form_valid(self, form):
        messages.success(self.request, _('Banner created successfully.'))
        return super().form_valid(form)


class DashboardBannerUpdateView(StaffRequiredMixin, UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'pages/dashboard/banner_form.html'
    success_url = reverse_lazy('dashboard:partners')

    def form_valid(self, form):
        messages.success(self.request, _('Banner updated successfully.'))
        return super().form_valid(form)


class DashboardBannerDeleteView(StaffRequiredMixin, DeleteView):
    model = Banner
    template_name = 'pages/dashboard/banner_confirm_delete.html'
    success_url = reverse_lazy('dashboard:partners')

    def form_valid(self, form):
        messages.success(self.request, _('Banner deleted successfully.'))
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Content CRUD
# ──────────────────────────────────────────────


class ContentPageForm(forms.ModelForm):
    class Meta:
        model = ContentPage
        fields = ['slug', 'page_type', 'title', 'title_en', 'content', 'content_en',
                  'meta_description', 'is_published']
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'page_type': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'title_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'content': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 8}),
            'content_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 8}),
            'meta_description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
        }


class DashboardContentPageCreateView(StaffRequiredMixin, CreateView):
    model = ContentPage
    form_class = ContentPageForm
    template_name = 'pages/dashboard/content_page_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Content page created successfully.'))
        return super().form_valid(form)


class DashboardContentPageUpdateView(StaffRequiredMixin, UpdateView):
    model = ContentPage
    form_class = ContentPageForm
    template_name = 'pages/dashboard/content_page_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Content page updated successfully.'))
        return super().form_valid(form)


class DashboardContentPageDeleteView(StaffRequiredMixin, DeleteView):
    model = ContentPage
    template_name = 'pages/dashboard/content_page_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content')

    def form_valid(self, form):
        messages.success(self.request, _('Content page deleted successfully.'))
        return super().form_valid(form)


class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = ['title', 'title_en', 'slug', 'short_text', 'short_text_en',
                  'full_text', 'full_text_en', 'image', 'published_at',
                  'is_published', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'title_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'short_text': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 4}),
            'short_text_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 4}),
            'full_text': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 8}),
            'full_text_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 8}),
            'image': forms.FileInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'type': 'datetime-local'}),
        }


class DashboardNewsCreateView(StaffRequiredMixin, CreateView):
    model = NewsItem
    form_class = NewsItemForm
    template_name = 'pages/dashboard/news_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('News item created successfully.'))
        return super().form_valid(form)


class DashboardNewsUpdateView(StaffRequiredMixin, UpdateView):
    model = NewsItem
    form_class = NewsItemForm
    template_name = 'pages/dashboard/news_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('News item updated successfully.'))
        return super().form_valid(form)


class DashboardNewsDeleteView(StaffRequiredMixin, DeleteView):
    model = NewsItem
    template_name = 'pages/dashboard/news_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content')

    def form_valid(self, form):
        messages.success(self.request, _('News item deleted successfully.'))
        return super().form_valid(form)


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'title_en', 'slug', 'department', 'city',
                  'short_description', 'full_description', 'requirements',
                  'salary_from', 'salary_to', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'title_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'department': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'city': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'short_description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 4}),
            'full_description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 8}),
            'requirements': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 6}),
            'salary_from': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'salary_to': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.all()
        self.fields['city'].required = False


class DashboardVacancyCreateView(StaffRequiredMixin, CreateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'pages/dashboard/vacancy_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Vacancy created successfully.'))
        return super().form_valid(form)


class DashboardVacancyUpdateView(StaffRequiredMixin, UpdateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'pages/dashboard/vacancy_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Vacancy updated successfully.'))
        return super().form_valid(form)


class DashboardVacancyDeleteView(StaffRequiredMixin, DeleteView):
    model = Vacancy
    template_name = 'pages/dashboard/vacancy_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content')

    def form_valid(self, form):
        messages.success(self.request, _('Vacancy deleted successfully.'))
        return super().form_valid(form)


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'question_en', 'answer', 'answer_en',
                  'category', 'order', 'is_published']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'question_en': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'answer': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 5}),
            'answer_en': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 5}),
            'category': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'order': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }


class DashboardFAQCreateView(StaffRequiredMixin, CreateView):
    model = FAQ
    form_class = FAQForm
    template_name = 'pages/dashboard/faq_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('FAQ created successfully.'))
        return super().form_valid(form)


class DashboardFAQUpdateView(StaffRequiredMixin, UpdateView):
    model = FAQ
    form_class = FAQForm
    template_name = 'pages/dashboard/faq_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('FAQ updated successfully.'))
        return super().form_valid(form)


class DashboardFAQDeleteView(StaffRequiredMixin, DeleteView):
    model = FAQ
    template_name = 'pages/dashboard/faq_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content')

    def form_valid(self, form):
        messages.success(self.request, _('FAQ deleted successfully.'))
        return super().form_valid(form)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['author_name', 'author_company', 'text', 'rating',
                  'is_approved', 'source']
        widgets = {
            'author_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'author_company': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'text': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 5}),
            'rating': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'source': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
        }


class DashboardReviewCreateView(StaffRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'pages/dashboard/review_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Review created successfully.'))
        return super().form_valid(form)


class DashboardReviewUpdateView(StaffRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'pages/dashboard/review_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Review updated successfully.'))
        return super().form_valid(form)


class DashboardReviewDeleteView(StaffRequiredMixin, DeleteView):
    model = Review
    template_name = 'pages/dashboard/review_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content')

    def form_valid(self, form):
        messages.success(self.request, _('Review deleted successfully.'))
        return super().form_valid(form)


class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        fields = ['title', 'slug', 'description', 'deadline', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 8}),
            'deadline': forms.DateTimeInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'type': 'datetime-local'}),
        }


class DashboardTenderCreateView(StaffRequiredMixin, CreateView):
    model = Tender
    form_class = TenderForm
    template_name = 'pages/dashboard/tender_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Tender created successfully.'))
        return super().form_valid(form)


class DashboardTenderUpdateView(StaffRequiredMixin, UpdateView):
    model = Tender
    form_class = TenderForm
    template_name = 'pages/dashboard/tender_form.html'
    success_url = reverse_lazy('dashboard:content')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Tender updated successfully.'))
        return super().form_valid(form)


class DashboardTenderDeleteView(StaffRequiredMixin, DeleteView):
    model = Tender
    template_name = 'pages/dashboard/tender_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content')

    def form_valid(self, form):
        messages.success(self.request, _('Tender deleted successfully.'))
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Order CRUD
# ──────────────────────────────────────────────

from apps.orders.models import Order, OrderStatusHistory


class DashboardOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'sender_name', 'sender_phone', 'recipient_name', 'recipient_phone',
                  'cargo_description', 'weight', 'length', 'width', 'height', 'declared_value', 'total_price',
                  'is_fragile', 'is_dangerous', 'is_temperature_sensitive']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'sender_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'sender_phone': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'recipient_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'recipient_phone': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm'}),
            'cargo_description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'rows': 3}),
            'weight': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'length': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'declared_value': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
            'total_price': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2.5 px-3 text-sm', 'step': '0.01'}),
        }


class DashboardOrderDetailView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        context['order'] = order
        context['status_history'] = order.status_history.all().order_by('-timestamp')
        from apps.orders.routing import get_simulation_flow
        context['simulation_flow'] = get_simulation_flow(order)
        return context


class DashboardOrderUpdateView(StaffRequiredMixin, UpdateView):
    model = Order
    form_class = DashboardOrderForm
    template_name = 'pages/dashboard/order_form.html'
    success_url = reverse_lazy('dashboard:orders')

    def form_valid(self, form):
        old_status = self.object.status
        new_status = form.cleaned_data.get('status')
        messages.success(self.request, _('Order updated successfully.'))
        response = super().form_valid(form)
        if old_status != new_status:
            OrderStatusHistory.objects.create(
                order=self.object,
                status=new_status,
                changed_by=self.request.user,
                comment=_('Status changed from %(old)s to %(new)s') % {'old': old_status, 'new': new_status},
            )
        return response


class DashboardOrderDeleteView(StaffRequiredMixin, DeleteView):
    model = Order
    template_name = 'pages/dashboard/order_confirm_delete.html'
    success_url = reverse_lazy('dashboard:orders')

    def form_valid(self, form):
        messages.success(self.request, _('Order deleted successfully.'))
        return super().form_valid(form)


from apps.orders.routing import simulate_next_status


class DashboardOrderSimulateView(StaffRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        next_status = simulate_next_status(order)
        if next_status is None:
            return JsonResponse({'status': order.status, 'complete': True})

        order.status = next_status
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status=next_status,
            changed_by=request.user,
            comment=_('Simulation: auto-advanced to %(status)s') % {'status': next_status},
        )

        return JsonResponse({
            'status': next_status,
            'status_label': dict(Order.Status.choices).get(next_status, next_status),
            'complete': next_status == 'delivered',
        })
