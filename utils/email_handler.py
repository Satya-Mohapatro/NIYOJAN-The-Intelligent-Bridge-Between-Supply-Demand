import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_report(recipients, report_text):
    """
    Sends the generated report to one or more email addresses.
    """
    sender_email = "niyojan.project.bot@gmail.com"  # optional dummy sender
    sender_password = "your_app_password"           # if you use Gmail app password

    # If no email credentials, skip sending (offline mode)
    if not sender_password:
        print("Email sending disabled: no credentials configured.")
        return False

    # Compose email
    subject = "Niyojan Inventory Report"
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(report_text, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        print(f"Report sent to {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
