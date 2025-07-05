from django.contrib import admin
from .models import Client, Message, Mailing
from django.contrib import admin
from .models import Attempt


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner", "created_at")
    search_fields = ("subject", "body")


admin.site.register(Client)
admin.site.register(Mailing)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "status", "time")
    list_filter = ("status", "time")
    search_fields = ("mailing__message__subject", "server_response")
