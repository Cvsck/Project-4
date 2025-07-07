from django.urls import path
from .views import (
    # 👥 Клиенты
    ClientListView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    # 💬 Сообщения
    MessageListView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    # 📤 Рассылки
    MailingListView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    MailingLogView,
    send_mailing_now,
    force_complete_mailing,  # ✅ добавлено
)

app_name = "mailing"

urlpatterns = [
    # 👥 Клиенты
    path("clients/", ClientListView.as_view(), name="client-list"),
    path("clients/create/", ClientCreateView.as_view(), name="client-create"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client-edit"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client-delete"),

    # 💬 Сообщения
    path("messages/", MessageListView.as_view(), name="message-list"),
    path("messages/create/", MessageCreateView.as_view(), name="message-create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message-edit"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message-delete"),

    # 📤 Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing-list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing-create"),
    path("mailings/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing-edit"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing-delete"),

    # 📤 Дополнительные действия
    path("mailings/<int:pk>/send/", send_mailing_now, name="mailing-send"),
    path("mailings/<int:pk>/logs/", MailingLogView.as_view(), name="mailing-logs"),
    path("mailings/<int:pk>/force-complete/", force_complete_mailing, name="force-complete"),  # ✅ добавлено
]
