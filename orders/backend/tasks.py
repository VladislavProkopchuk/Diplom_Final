from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_mail(subject, body, from_email, to_email):
    msg = EmailMultiAlternatives(subject, body, from_email, to_email)
    msg.send()
