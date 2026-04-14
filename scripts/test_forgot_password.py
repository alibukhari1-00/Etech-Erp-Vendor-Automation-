import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import datetime

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.crud import user_otp as user_otp_crud
from app.models.user_otp import UserOTP
from app.core.mail import send_otp_email

class TestForgotPasswordFlow(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.email = "test@example.com"

    @patch("app.crud.user_otp.random.choices")
    def test_create_otp(self, mock_choices):
        mock_choices.return_value = ["1", "2", "3", "4", "5", "6"]
        
        otp_record = user_otp_crud.create_otp(self.db, self.email)
        
        self.assertEqual(otp_record.email, self.email)
        self.assertEqual(otp_record.otp, "123456")
        self.assertTrue(otp_record.expires_at > datetime.datetime.now(datetime.timezone.utc))
        self.db.add.assert_called_once()
        self.db.commit.assert_called()

    @patch("smtplib.SMTP")
    def test_send_otp_email_mock(self, mock_smtp):
        # Test with settings enabled (mocked)
        with patch("app.core.mail.settings") as mock_settings:
            mock_settings.SMTP_USER = "user"
            mock_settings.SMTP_PASSWORD = "pass"
            mock_settings.SMTP_HOST = "localhost"
            mock_settings.SMTP_PORT = 587
            mock_settings.SMTP_TLS = True
            mock_settings.EMAILS_FROM_NAME = "Test"
            mock_settings.EMAILS_FROM_EMAIL = "test@test.com"
            
            result = send_otp_email(self.email, "123456")
            self.assertTrue(result)
            mock_smtp.return_value.__enter__.return_value.login.assert_called_once_with("user", "pass")

    def test_otp_expiration(self):
        past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
        otp_record = UserOTP(email=self.email, otp="123456", expires_at=past_time)
        self.assertTrue(otp_record.is_expired())
        
        future_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
        otp_record2 = UserOTP(email=self.email, otp="123456", expires_at=future_time)
        self.assertFalse(otp_record2.is_expired())

if __name__ == "__main__":
    unittest.main()
