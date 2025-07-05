from django.db import models
from django.conf import settings
from django.utils import timezone


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients"
    )

    class Meta:
        permissions = [
            ("can_manage_clients", "Может управлять клиентами"),
        ]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("can_manage_messages", "Может управлять сообщениями"),
        ]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    PERIOD_CHOICES = [
        ("daily", "Ежедневно"),
        ("weekly", "Еженедельно"),
        ("monthly", "Ежемесячно"),
    ]

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "В процессе"),
        ("completed", "Завершена"),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    periodicity = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")

    class Meta:
        permissions = [
            ("can_manage_mailings", "Может управлять рассылками"),
        ]
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка #{self.pk} — {self.message.subject}"


class Attempt(models.Model):
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, related_name="attempts"
    )
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20, choices=[("success", "Успешно"), ("error", "Ошибка")]
    )
    server_response = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"

    def __str__(self):
        return f"{self.mailing} — {self.status} — {self.time.strftime('%Y-%m-%d %H:%M:%S')}"
