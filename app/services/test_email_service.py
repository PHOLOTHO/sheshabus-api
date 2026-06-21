import os
import sys
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.services.email_service import EmailService

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG)


def test_email_delivery():
    """Simple test to see if emails can be sent"""

    # Create the app
    app = create_app()

    with app.app_context():
        print("🧪 Testing Email Delivery...")
        print("=" * 50)

        # Print current email configuration
        print(f"📧 Mail Server: {app.config.get('MAIL_SERVER')}")
        print(f"📧 Mail Port: {app.config.get('MAIL_PORT')}")
        print(f"📧 Mail Username: {app.config.get('MAIL_USERNAME')}")
        print(f"📧 Using TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"📧 Using SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"🌐 Frontend URL: {app.config.get('FRONTEND_URL')}")

        print("\n📨 Attempting to send test email...")

        # Test data
        test_email = "lpholotho@gmail.com"  # Your email
        test_name = "Lucas Test"
        test_token = "test-token-abc-123"

        try:
            # Test 1: Send verification email
            print("\n1. Testing verification email...")
            success = EmailService.send_verification_email(test_email, test_name, test_token)

            if success:
                print("✅ Email service returned SUCCESS")
                print("📧 Check your email inbox (and spam folder)")
            else:
                print("❌ Email service returned FAILED")

        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            print("\n🔍 Detailed error information:")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 50)
        print("Test completed!")


if __name__ == '__main__':
    test_email_delivery()