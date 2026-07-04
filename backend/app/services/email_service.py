import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL

    def send_otp_email(self, to_email: str, otp_code: str):
        if not self.user or not self.password:
            # Fallback to console if SMTP is not configured
            logger.warning("SMTP credentials not configured. Printing OTP to console.")
            print(f"\n{'='*40}\n[MOCK EMAIL TO {to_email}]\nYour OTP Code is: {otp_code}\n{'='*40}\n")
            return

        subject = "DocuChat Enterprise - Verification Code"
        body = f"""
        Hello,
        
        Your verification code for DocuChat Enterprise is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you did not request this, please ignore this email.
        """

        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            logger.info(f"OTP email successfully sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise Exception("Could not send email")

    def send_welcome_email(self, to_email: str, temp_password: str):
        if not self.user or not self.password:
            logger.warning("SMTP credentials not configured. Printing Welcome Email to console.")
            print(f"\n{'='*40}\n[MOCK EMAIL TO {to_email}]\nWelcome! Your temporary password is: {temp_password}\n{'='*40}\n")
            return

        subject = "Welcome to DocuChat Enterprise"
        body = f"""
        Hello,
        
        An administrator has created an account for you on DocuChat Enterprise.
        
        Your login email: {to_email}
        Your temporary password: {temp_password}
        
        Upon your first login, you will be required to change your password.
        
        Best regards,
        The DocuChat Team
        """

        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Welcome email successfully sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {e}")
            raise Exception("Could not send welcome email")

email_service = EmailService()
