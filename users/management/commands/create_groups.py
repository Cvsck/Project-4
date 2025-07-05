from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Message, Client, Mailing


class Command(BaseCommand):
    help = "Создаёт группу 'Менеджеры' и назначает ей права на модели рассылок"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Менеджеры")
        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' создана"))
        else:
            self.stdout.write(self.style.WARNING("Группа 'Менеджеры' уже существует"))

        models = [Message, Client, Mailing]
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            for perm in permissions:
                group.permissions.add(perm)
                self.stdout.write(f"Добавлено право: {perm.codename}")
