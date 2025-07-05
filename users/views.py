from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


# 🔐 Вход
class UserLoginView(LoginView):
    template_name = "users/login.html"


# 🚪 Выход
class UserLogoutView(LogoutView):
    next_page = reverse_lazy("home")


# 📝 Регистрация
class UserRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")


# 👤 Профиль
class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"


# ✏️ Редактирование профиля
class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлён.")
        return super().form_valid(form)
