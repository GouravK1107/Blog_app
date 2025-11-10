import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOTP

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10

def generate_otp(length=OTP_LENGTH):
    # numeric OTP (0-9). Avoid leading zeros issues by formatting.
    range_start = 10**(length-1)
    range_end = (10**length) - 1
    return str(random.randint(range_start, range_end))

def create_and_send_otp(user, target_email, subject_prefix='Your BlogApp OTP'):
    # create otp object and send mail synchronously
    otp_plain = generate_otp()
    now = timezone.now()
    otp_obj = EmailOTP.objects.create(
        user=user,
        email=target_email,
        expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    otp_obj.set_code(otp_plain)
    otp_obj.save()

    subject = f"{subject_prefix}: Verification code"
    message = (
        f"Your verification code is: {otp_plain}\n\n"
        f"This code will expire in {OTP_EXPIRY_MINUTES} minutes.\n\n"
        "If you didn't request this, ignore this email."
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    # send_mail returns number of successfully delivered messages
    send_mail(subject, message, from_email, [target_email], fail_silently=False)
    return otp_obj