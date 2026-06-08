from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView, DeleteView, CreateView, ListView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django import forms

User = get_user_model()


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role in ['admin', 'manager']

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('dashboard:login')
        return redirect('core:home')


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
        try:
            from apps.services.models import ServiceCategory, Service, AdditionalService, Tariff
            context['categories'] = ServiceCategory.objects.all()
            context['services'] = Service.objects.all()[:50]
            context['additional_services'] = AdditionalService.objects.all()
            context['tariffs'] = Tariff.objects.all()
        except ImportError:
            context['categories'] = []
            context['services'] = []
            context['additional_services'] = []
            context['tariffs'] = []
        return context


class DashboardContentListView(StaffRequiredMixin, TemplateView):
    template_name = 'pages/dashboard/content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.core.models import ContentPage, NewsItem, Vacancy, FAQ, Review, Tender
            context['pages'] = ContentPage.objects.all()[:50]
            context['news'] = NewsItem.objects.all()[:20]
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
