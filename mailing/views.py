from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page, never_cache
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from .models import Message, Client, Mailing, Attempt
from .forms import MessageForm, ClientForm, MailingForm
from django.db.models import F


# 🏠 Главная страница со статистикой
@method_decorator(never_cache, name="dispatch")
class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["mailing_count"] = Mailing.objects.count()
        context["active_mailing_count"] = Mailing.objects.filter(status="Запущена").count()

        # ✅ Только email клиентов, исключая тех, у кого email совпадает с владельцем
        context["unique_recipient_emails"] = (
            Client.objects.exclude(email=F("owner__email"))
            .filter(mailing__isnull=False)
            .values_list("email", flat=True)
            .distinct()
        )

        context["unique_recipient_count"] = context["unique_recipient_emails"].count()

        return context



# 📬 Сообщения
@method_decorator(cache_control(public=True, max_age=300), name="dispatch")
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Сообщение успешно создано.")
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message-list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Сообщение успешно обновлено.")
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message-list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Сообщение удалено.")
        return super().delete(request, *args, **kwargs)


# 👥 Клиенты
@method_decorator(cache_control(public=True, max_age=300), name="dispatch")
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):  # ✅ модератор видит всех клиентов
        if self.request.user.is_staff:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)



class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client-list")

    def form_valid(self, form):
        # ❗ Запрещаем добавлять самого себя как клиента
        if form.cleaned_data["email"] == self.request.user.email:
            form.add_error("email", "Нельзя добавить самого себя как клиента.")
            return self.form_invalid(form)

        # ✅ Привязываем клиента к текущему пользователю
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client-list")

    def get_queryset(self):
        if self.request.user.is_staff:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Данные клиента обновлены.")
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client-list")

    def get_queryset(self):
        if self.request.user.is_staff:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Клиент удалён.")
        return super().delete(request, *args, **kwargs)



# 📤 Рассылки
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):  # ✅ модератор видит все рассылки
        if self.request.user.is_staff:
            return Mailing.objects.all().order_by("-start_time")
        return Mailing.objects.filter(owner=self.request.user).order_by("-start_time")



@method_decorator(cache_control(public=True, max_age=300), name="dispatch")
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing-list")

    def get_form_kwargs(self):  # ✅ передаём пользователя в форму
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Рассылка успешно создана.")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing-list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):  # ✅ тоже передаём пользователя
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Рассылка обновлена.")
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing-list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Рассылка удалена.")
        return super().delete(request, *args, **kwargs)


# 🚀 Ручной запуск рассылки
from django.contrib.auth.decorators import login_required

# 🚀 Ручной запуск рассылки
@login_required
def send_mailing_now(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # 🔐 Проверка доступа: только владелец или модератор
    if not request.user.is_staff and mailing.owner != request.user:
        messages.error(request, "У вас нет доступа к этой рассылке.")
        return redirect("mailing:mailing-list")

    if mailing.status == "Завершена":  # ✅ защита от повторной отправки
        messages.warning(request, "Нельзя отправить завершённую рассылку.")
        return redirect("mailing:mailing-list")

    success = True
    response_log = ""

    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
                fail_silently=False,
            )
            response_log += f"✅ {client.email} — отправлено\n"
        except Exception as e:
            success = False
            response_log += f"❌ {client.email} — ошибка: {str(e)}\n"

    Attempt.objects.create(
        mailing=mailing,
        status="success" if success else "error",
        server_response=response_log,
    )

    messages.success(request, "Рассылка выполнена. См. лог попыток.")
    return redirect("mailing:mailing-list")



# 📄 Просмотр логов рассылки
class MailingLogView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_logs.html"
    context_object_name = "mailing"

    def get_queryset(self):
        if self.request.user.is_staff:  # ✅ модератор видит все логи
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.order_by("-time")
        return context


# ⛔ Принудительное завершение рассылки
@staff_member_required
def force_complete_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.status = "Завершена"
    mailing.save()
    messages.success(request, "Рассылка принудительно завершена.")
    return redirect("mailing:mailing-list")
