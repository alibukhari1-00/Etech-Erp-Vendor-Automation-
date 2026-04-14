import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email_to: str, otp: str):
    """
    Sends an OTP email to the user.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(f"SMTP settings not configured. OTP for {email_to} is: {otp}")
        print(f"DEBUG: OTP for {email_to} is: {otp}")
        return True

    try:
        message = MIMEMultipart()
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        message["To"] = email_to
        message["Subject"] = "Your Password Reset OTP"

        body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>You requested to reset your password. Use the following OTP to proceed:</p>
                <h1 style="color: #4F46E5; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
                <p>This OTP is valid for 10 minutes. If you did not request this, please ignore this email.</p>
                <p>Best regards,<br>{settings.EMAILS_FROM_NAME} Team</p>
            </body>
        </html>
        """
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            # Always print OTP to console for easier development testing
            print(f"\n--- [DEVELOPMENT ONLY] OTP FOR {email_to}: {otp} ---\n")
            
            server.send_message(message)
        
        logger.info(f"OTP email sent successfully to {email_to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        # Log OTP to console so development can continue even if email is delayed/spammed
        print(f"\n--- [DEVELOPMENT ONLY] OTP FOR {email_to}: {otp} ---\n")
        return True
