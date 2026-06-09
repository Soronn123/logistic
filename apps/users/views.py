from decimal import Decimal, InvalidOperation

from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView, View

from .forms import CargoTemplateForm, ContactTemplateForm, DeliveryTemplateForm, LoginForm, PasswordChangeForm, ProfileForm, RegisterForm, TicketForm, TicketMessageForm
from .models import CargoTemplate, ContactTemplate, CustomUser, DeliveryTemplate, Ticket, TicketMessage, Transaction


class LoginView(AuthLoginView):
    form_class = LoginForm
    template_name = 'pages/users/login.html'


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('core:home')


class RegisterView(CreateView):
    model = CustomUser
    form_class = RegisterForm
    template_name = 'pages/users/register.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_count'] = self.request.user.orders.count()
        context['tickets_count'] = self.request.user.tickets.filter(status__in=['open', 'in_progress']).count()
        context['recent_transactions'] = Transaction.objects.filter(user=self.request.user)[:5]
        return context


class ProfileSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/users/settings.html'

    def get(self, request, *args, **kwargs):
        profile_form = ProfileForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)
        return self.render_to_response(self.get_context_data(profile_form=profile_form, password_form=password_form))

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'profile':
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
            password_form = PasswordChangeForm(user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, _('Profile updated successfully.'))
                return redirect('users:settings')
        elif action == 'password':
            profile_form = ProfileForm(instance=request.user)
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, _('Password changed successfully.'))
                return redirect('users:settings')
        else:
            profile_form = ProfileForm(instance=request.user)
            password_form = PasswordChangeForm(user=request.user)
        return self.render_to_response(self.get_context_data(profile_form=profile_form, password_form=password_form))


class BalanceView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'pages/users/balance.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class BalanceTopUpView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/users/balance_topup.html'

    def get(self, request, *args, **kwargs):
        return redirect('users:balance')

    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount)
            if amount > Decimal('0'):
                user = request.user
                user.balance += amount
                user.save()
                Transaction.objects.create(
                    user=user,
                    amount=amount,
                    transaction_type='deposit',
                    description=_('Balance top-up'),
                    balance_after=user.balance,
                )
            return redirect('users:balance_success')
        except (InvalidOperation, ValueError, TypeError):
            return redirect('users:balance')


class BalanceSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/users/balance_success.html'


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'pages/users/tickets.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        qs = Ticket.objects.filter(created_by=self.request.user)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'pages/users/ticket_create.html'
    success_url = reverse_lazy('users:tickets')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        message = form.cleaned_data.get('message', '')
        if message:
            TicketMessage.objects.create(
                ticket=self.object,
                sender=self.request.user,
                message=message,
            )
        return response


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'pages/users/ticket_detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        return Ticket.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TicketMessageForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TicketMessageForm(request.POST)
        if form.is_valid():
            TicketMessage.objects.create(
                ticket=self.object,
                sender=request.user,
                message=form.cleaned_data['message'],
            )
        return self.get(request, *args, **kwargs)


class OrderListView(LoginRequiredMixin, ListView):
    model = None
    template_name = 'pages/users/orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        from apps.orders.models import Order
        qs = Order.objects.filter(user=self.request.user)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = None
    template_name = 'pages/users/order_detail.html'
    context_object_name = 'order'
    slug_field = 'tracking_number'
    slug_url_kwarg = 'tracking_number'

    def get_queryset(self):
        from apps.orders.models import Order
        return Order.objects.filter(user=self.request.user)


class AccountingDocumentsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/users/accounting_docs.html'


class TemplatesView(LoginRequiredMixin, ListView):
    model = None
    template_name = 'pages/users/templates.html'
    context_object_name = 'templates'

    def get_queryset(self):
        from .models import ContactTemplate
        return ContactTemplate.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.geo.models import City
        from apps.services.models import Service, AdditionalService
        context['delivery_templates'] = DeliveryTemplate.objects.filter(user=self.request.user)
        context['cargo_templates'] = CargoTemplate.objects.filter(user=self.request.user)
        context['delivery_form'] = DeliveryTemplateForm()
        context['contact_form'] = ContactTemplateForm()
        context['cargo_form'] = CargoTemplateForm()
        context['cities'] = City.objects.filter(is_active=True)
        context['services'] = Service.objects.filter(is_active=True)
        context['additional_services'] = AdditionalService.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        from .models import ContactTemplate
        action = request.POST.get('action')
        if action == 'delete':
            pk = request.POST.get('pk')
            if pk:
                ContactTemplate.objects.filter(pk=pk, user=request.user).delete()
            return self.get(request, *args, **kwargs)
        elif action == 'edit_contact':
            pk = request.POST.get('pk')
            template = get_object_or_404(ContactTemplate, pk=pk, user=request.user)
            form = ContactTemplateForm(request.POST, instance=template)
            if form.is_valid():
                form.save()
                from django.contrib import messages
                messages.success(request, _('Contact template updated successfully.'))
            return redirect('users:templates')
        elif action == 'delete_delivery':
            pk = request.POST.get('pk')
            if pk:
                DeliveryTemplate.objects.filter(pk=pk, user=request.user).delete()
            return self.get(request, *args, **kwargs)
        elif action == 'create_delivery':
            form = DeliveryTemplateForm(request.POST)
            if form.is_valid():
                template = form.save(commit=False)
                template.user = request.user
                template.save()
                form.save_m2m()
                from django.contrib import messages
                messages.success(request, _('Delivery template created successfully.'))
            return redirect('users:templates')
        elif action == 'edit_delivery':
            pk = request.POST.get('pk')
            template = get_object_or_404(DeliveryTemplate, pk=pk, user=request.user)
            form = DeliveryTemplateForm(request.POST, instance=template)
            if form.is_valid():
                form.save()
                from django.contrib import messages
                messages.success(request, _('Delivery template updated successfully.'))
            return redirect('users:templates')
        elif action == 'delete_cargo':
            pk = request.POST.get('pk')
            if pk:
                CargoTemplate.objects.filter(pk=pk, user=request.user).delete()
            return self.get(request, *args, **kwargs)
        elif action == 'create_cargo':
            form = CargoTemplateForm(request.POST)
            if form.is_valid():
                template = form.save(commit=False)
                template.user = request.user
                template.save()
                from django.contrib import messages
                messages.success(request, _('Cargo template created successfully.'))
            return redirect('users:templates')
        elif action == 'edit_cargo':
            pk = request.POST.get('pk')
            template = get_object_or_404(CargoTemplate, pk=pk, user=request.user)
            form = CargoTemplateForm(request.POST, instance=template)
            if form.is_valid():
                form.save()
                from django.contrib import messages
                messages.success(request, _('Cargo template updated successfully.'))
            return redirect('users:templates')
        return self.get(request, *args, **kwargs)


class DeliveryTemplateEditView(LoginRequiredMixin, UpdateView):
    model = DeliveryTemplate
    form_class = DeliveryTemplateForm
    template_name = 'pages/users/template_edit.html'
    success_url = reverse_lazy('users:templates')

    def get_queryset(self):
        return DeliveryTemplate.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.geo.models import City
        from apps.services.models import Service, AdditionalService
        context['cities'] = City.objects.filter(is_active=True)
        context['services'] = Service.objects.filter(is_active=True)
        context['additional_services'] = AdditionalService.objects.all()
        context['template_addon_ids'] = list(self.object.additional_services.values_list('id', flat=True)) if self.object.pk else []
        return context
