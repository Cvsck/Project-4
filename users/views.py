from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, TemplateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from .models import CustomUser


# 🔐 Вход
class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = CustomAuthenticationForm


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


# 👮 Список всех пользователей (только для модераторов с правом can_block_user)
class UserListView(PermissionRequiredMixin, ListView):
    model = get_user_model()
    template_name = "users/user_list.html"
    context_object_name = "users"
    permission_required = "users.can_block_user"


# ⛔ Блокировка пользователя (только для модераторов с правом can_block_user)
@permission_required("users.can_block_user")
def block_user(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    user.is_blocked = True
    user.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "blocked"})
    messages.success(request, f"Пользователь {user.email} заблокирован.")
    return redirect("users:user-list")

@permission_required("users.can_block_user")
def unblock_user(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    user.is_blocked = False
    user.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "unblocked"})
    messages.success(request, f"Пользователь {user.email} разблокирован.")
    return redirect("users:user-list")
