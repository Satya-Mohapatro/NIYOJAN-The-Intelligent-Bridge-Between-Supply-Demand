import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from utils.email_handler import send_email_report
from dotenv import load_dotenv

load_dotenv()

def test_email():
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    
    print(f"SMTP_EMAIL present: {bool(sender)}")
    print(f"SMTP_PASSWORD present: {bool(password)}")
    
    if not sender or not password:
        print("Skipping actual send test due to missing credentials.")
        return

    print("Attempting to send test email...")
    # Using the sender as recipient for safety
    try:
        success = send_email_report(
            recipients=[sender],
            subject="Test Email from Niyojan Debugger",
            body="This is a test email to verify the fix.",
            attachments=None
        )
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email failed to send (check logic/creds).")
    except TypeError as e:
        print(f"❌ TypeError (Signature Mismatch?): {e}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_email()
