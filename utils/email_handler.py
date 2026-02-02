import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

def send_email_report(recipients, subject, body, attachments=None):
    """
    Sends an email with optional attachments.
    recipients: list of email strings
    subject: str
    body: str
    attachments: list of file paths (optional)
    """
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not sender_password:
        print("Email sending disabled: SMTP_EMAIL or SMTP_PASSWORD not set.")
        return False

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if attachments:
        for filepath in attachments:
            try:
                with open(filepath, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                msg.attach(part)
            except Exception as e:
                print(f"Failed to attach {filepath}: {e}")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        print(f"Report sent to {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
