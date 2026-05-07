from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import CreateView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import Profile
from orders.models import Order

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        
        # Save phone number to profile
        phone = self.request.POST.get('phone', '')
        if phone:
            profile, created = Profile.objects.get_or_create(user=self.object)
            profile.phone = phone
            profile.save()
            
        messages.success(self.request, 'Регистрация прошла успешно!')
        return response


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = '/'
    
    def get_success_url(self):
        # Check if there's a 'next' parameter in the request
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url
        # Otherwise, use the default success URL
        return super().get_success_url()
    
    def form_valid(self, form):
        # Call the parent's form_valid method to perform the actual login
        response = super().form_valid(form)
        # Return the response which should include the redirect
        return response


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'Вы успешно вышли из системы.')
        return HttpResponseRedirect(reverse('products:product_list'))


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user).prefetch_related('items__product')
        return context


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)