import os
import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart


def send_email(sender_email: str, recipients: list, subject: str, body: str):
    # Create the message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Set up the SMTP server
    smtp_server = "smtp.mail.me.com"
    smtp_port = 587
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not (smtp_user and smtp_password):
        raise RuntimeError(
            "SMTP_USER and SMTP_PASSWORD environment variables must be set"
        )

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(sender_email, recipients, msg.as_string())
    server.quit()
