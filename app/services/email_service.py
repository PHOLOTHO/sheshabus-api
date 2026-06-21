from flask_mail import Message
from app import mail
from flask import current_app
import logging

# Set up logging
logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_verification_email(email, name, token):
        try:
            logger.info(f"🔍 DEBUG: Starting email send to {email}")

            # Check if we're in app context
            if not current_app:
                logger.error("❌ DEBUG: No Flask app context!")
                return False

            # Log email configuration
            logger.info(f"🔍 DEBUG: Mail server: {current_app.config.get('MAIL_SERVER')}")
            logger.info(f"🔍 DEBUG: Mail port: {current_app.config.get('MAIL_PORT')}")
            logger.info(f"🔍 DEBUG: Mail username: {current_app.config.get('MAIL_USERNAME')}")
            logger.info(f"🔍 DEBUG: Mail use TLS: {current_app.config.get('MAIL_USE_TLS')}")
            logger.info(f"🔍 DEBUG: Frontend URL: {current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}")

            # Use FRONTEND_URL from config
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            verification_url = f"{frontend_url}/verify-email?token={token}"

            logger.info(f"🔍 DEBUG: Verification URL: {verification_url}")

            msg = Message(
                subject='Verify Your SheShaBus Account',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )

            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>SheShaBus</h1>
                        <p>Email Verification</p>
                    </div>
                    <div class="content">
                        <h2>Hello {name},</h2>
                        <p>Thank you for registering with SheShaBus! Please verify your email address by clicking the button below:</p>
                        <p style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </p>
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p><code>{verification_url}</code></p>
                        <p>This verification link will expire in 24 hours.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 SheShaBus. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Add plain text version as fallback
            msg.body = f"""
            Hello {name},

            Thank you for registering with SheShaBus! Please verify your email address by visiting the following link:

            {verification_url}

            This verification link will expire in 24 hours.

            If you did not create an account, please ignore this email.

            Best regards,
            SheShaBus Team
            """

            logger.info(f"🔍 DEBUG: About to send email to {email}")
            mail.send(msg)
            logger.info(f"✅ Verification email sent successfully to {email}")
            return True

        except Exception as e:
            logger.error(f"❌ Verification email sending failed to {email}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_password_reset_email(email, name, token):
        try:
            logger.info(f"🔍 DEBUG: Starting password reset email send to {email}")

            # Check if we're in app context
            if not current_app:
                logger.error("❌ DEBUG: No Flask app context!")
                return False

            # Log email configuration
            logger.info(f"🔍 DEBUG: Mail server: {current_app.config.get('MAIL_SERVER')}")
            logger.info(f"🔍 DEBUG: Mail username: {current_app.config.get('MAIL_USERNAME')}")

            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            reset_url = f"{frontend_url}/reset-password?token={token}"

            logger.info(f"🔍 DEBUG: Reset URL: {reset_url}")

            msg = Message(
                subject='Reset Your SheShaBus Password',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )

            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #FF6B35; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #FF6B35; color: white; text-decoration: none; border-radius: 4px; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>SheShaBus</h1>
                        <p>Password Reset</p>
                    </div>
                    <div class="content">
                        <h2>Hello {name},</h2>
                        <p>We received a request to reset your password. Click the button below to create a new password:</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset Password</a>
                        </p>
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p><code>{reset_url}</code></p>
                        <p>This reset link will expire in 1 hour.</p>
                        <p>If you didn't request a password reset, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 SheShaBus. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Add plain text version
            msg.body = f"""
            Hello {name},

            We received a request to reset your password for your SheShaBus account.

            Please use the following link to reset your password:
            {reset_url}

            This link will expire in 1 hour.

            If you didn't request this reset, please ignore this email.

            Best regards,
            SheShaBus Team
            """

            logger.info(f"🔍 DEBUG: About to send password reset email to {email}")
            mail.send(msg)
            logger.info(f"✅ Password reset email sent successfully to {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Password reset email sending failed to {email}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def test_email_configuration():
        """Test method to verify email configuration is working"""
        try:
            logger.info("🧪 Testing email configuration...")

            # Check if we're in app context
            if not current_app:
                logger.error("❌ No Flask app context for test!")
                return "❌ No Flask app context"

            test_email = current_app.config['MAIL_USERNAME']
            test_name = "Test User"
            test_token = "test-token-123"

            logger.info(f"🔍 Test email: {test_email}")
            logger.info(f"🔍 Test name: {test_name}")
            logger.info(f"🔍 Test token: {test_token}")

            success = EmailService.send_verification_email(test_email, test_name, test_token)
            if success:
                result = f"✅ Test email sent successfully to {test_email}"
                logger.info(result)
                return result
            else:
                result = "❌ Failed to send test email"
                logger.error(result)
                return result
        except Exception as e:
            result = f"❌ Email configuration test failed: {str(e)}"
            logger.error(result)
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return result

    @staticmethod
    def send_notification_email(email, name, subject, message):
        """Generic method for sending notification emails"""
        try:
            logger.info(f"🔍 DEBUG: Starting notification email send to {email}")

            msg = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )

            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>SheShaBus</h1>
                        <p>Notification</p>
                    </div>
                    <div class="content">
                        <h2>Hello {name},</h2>
                        <p>{message}</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 SheShaBus. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            msg.body = f"""
            Hello {name},

            {message}

            Best regards,
            SheShaBus Team
            """

            mail.send(msg)
            logger.info(f"✅ Notification email sent successfully to {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Notification email sending failed to {email}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False