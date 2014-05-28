# utils.comms

# DJANGO
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_html_mail(subject, content_plain, content_html, recipients, sender=None):
    sender = sender or settings.VAVS_EMAIL_FROM
    msg = EmailMultiAlternatives(
        subject, 
        content_plain, 
        sender,
        recipients)
    msg.attach_alternative(content_html, "text/html")
    msg.send()
