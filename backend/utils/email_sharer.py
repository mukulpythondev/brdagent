import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
import config

logger = logging.getLogger(__name__)

def send_brd_email(to_email: str, project_name: str, pdf_bytes: bytes) -> bool:
    """
    Sends the generated BRD PDF document as an attachment to the specified recipient.
    Uses SMTP details configured in config.py.
    """
    host = config.SMTP_HOST
    port = config.SMTP_PORT
    username = config.SMTP_USERNAME
    password = config.SMTP_PASSWORD
    from_email = config.SMTP_FROM_EMAIL
    
    logger.info(f"Preparing to send BRD email for '{project_name}' to: {to_email}")
    
    # 1. Create the message container
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"Requirements Document Shared: {project_name}"
    
    # 2. Email Body text
    body = f"""
Hello,

A Business Requirements Document (BRD) for the project "{project_name}" has been shared with you from BRD Forge.

Please find the structured PDF report attached to this email.

Best Regards,
BRD Forge AI Assistant
    """
    msg.attach(MIMEText(body, 'plain'))
    
    # 3. Attach PDF bytes
    filename = f"{project_name.replace(' ', '_')}_Requirements.pdf"
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {filename}',
    )
    msg.attach(part)
    
    # 4. Connect to server and transmit
    try:
        # Check if port is 465 (SSL)
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            server.ehlo()
            # Upgrade connection to TLS if supported (port 587 / 25)
            if port == 587 or server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()
                
        # Login if username is configured
        if username and password:
            server.login(username, password)
            
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        logger.info(f"BRD PDF email successfully transmitted to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via SMTP {host}:{port}: {e}")
        # We do not crash the request, we just return False and let backend report the error.
        raise e
