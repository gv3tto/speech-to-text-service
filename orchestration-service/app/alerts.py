import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
import threading

from app.config import ALERT_EMAIL_FROM, ALERT_EMAIL_PASSWORD, ALERT_EMAIL_TO
from app.logger import get_logger

logger = get_logger("alerts")

def send_email_alert(alert_id: str, message: str):
    """
    Send an alert email in a background thread.
    
    threading.Thread runs the email sending in the background —
    the API responds immediately while the email sends separately.
    """
    if not ALERT_EMAIL_FROM or not ALERT_EMAIL_PASSWORD or not ALERT_EMAIL_TO:
        logger.warning("Email alerts not configured - skipping email notification")
        return
    
    thread = threading.Thread(
        target=_send_email,
        args=(alert_id, message)
    )
    thread.start()

def _send_email(alert_id: str, message: str):
    """
    Actually sends the email. Runs in a background thread.
    
    SMTP = Simple Mail Transfer Protocol — the standard way
    to send emails programmatically.
    """
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # build the email
        email = MIMEMultipart()
        email["From"] = ALERT_EMAIL_FROM
        email["To"] = ALERT_EMAIL_TO
        email["Subject"] = f"[ALERT] Speech-to-Text service - {alert_id}"

        # email body with details
        body = f"""
        Speech-to-Text Service Alert

        Alert Type: {alert_id}
        Time: {timestamp}

        Details:
        {message}
        """
        email.attach(MIMEText(body, "plain"))

        # connect to Gmail and send
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(ALERT_EMAIL_FROM, ALERT_EMAIL_PASSWORD)
            server.send_message(email)

            logger.info(f"Alert email sent: {alert_id}")

    except Exception as e:
        logger.error(f"Failed to send alert email: {str(e)}")  