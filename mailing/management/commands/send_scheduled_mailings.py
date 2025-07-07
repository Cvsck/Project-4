from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from mailing.models import Mailing, Attempt
from django.conf import settings


class Command(BaseCommand):
    help = "Отправляет все активные рассылки, запланированные на текущее время"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            status="created", start_time__lte=now, end_time__gte=now
        )

        for mailing in mailings:
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

            # Обновим статус рассылки, если она однократная
            if mailing.periodicity == "once":
                mailing.status = "completed"
                mailing.save()

        self.stdout.write(self.style.SUCCESS("Рассылки обработаны"))
