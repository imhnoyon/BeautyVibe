from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(email, code):
    subject = "Verify your email"
    message = f""" 
     Your verification code is: {code}
     This code will expire in 10 minutes.
      """
    send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False,)


def send_reset_password_email(email, code):
    subject = "Reset your password"
    message = f"""
     Your password reset code is: {code}
ss
     This code will expire in 10 minutes.
   """
    send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False,)
