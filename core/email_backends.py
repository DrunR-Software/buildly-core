"""
Custom email backends for SendGrid API, MailerSend API, and MailerSend SMTP
"""
import os
import logging
import smtplib
import base64
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address
from django.conf import settings

logger = logging.getLogger(__name__)


class SendGridAPIBackend(BaseEmailBackend):
    """
    SendGrid API email backend using their Web API v3
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None) or os.getenv('SENDGRID_API_KEY')
        
    def send_messages(self, email_messages):
        """
        Send multiple email messages using SendGrid API
        """
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("SendGrid API key not configured")
            return 0
            
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
        except ImportError:
            if not self.fail_silently:
                raise ImportError("SendGrid library not installed. Run: pip install sendgrid")
            logger.error("SendGrid library not installed")
            return 0
            
        sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        sent_count = 0
        
        for message in email_messages:
            try:
                # Convert Django email message to SendGrid format
                from_email = Email(sanitize_address(message.from_email, message.encoding)[1])
                
                # Handle multiple recipients
                for recipient in message.to:
                    to_email = To(sanitize_address(recipient, message.encoding)[1])
                    
                    # Create content (handle both HTML and plain text)
                    if message.content_subtype == 'html':
                        content = Content("text/html", message.body)
                    else:
                        content = Content("text/plain", message.body)
                    
                    # Create mail object
                    mail = Mail(from_email, to_email, message.subject, content)
                    
                    # Handle HTML alternative
                    if hasattr(message, 'alternatives') and message.alternatives:
                        for alternative in message.alternatives:
                            if alternative[1] == 'text/html':
                                mail.add_content(Content("text/html", alternative[0]))
                    
                    # Send email
                    response = sg.client.mail.send.post(request_body=mail.get())
                    
                    if response.status_code >= 200 and response.status_code < 300:
                        sent_count += 1
                        logger.info(f"Email sent successfully via SendGrid to {recipient}")
                    else:
                        logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
                        if not self.fail_silently:
                            raise Exception(f"SendGrid API error: {response.status_code}")
                            
            except Exception as e:
                logger.error(f"Error sending email via SendGrid: {e}")
                if not self.fail_silently:
                    raise
                    
        return sent_count


class MailerSendAPIBackend(BaseEmailBackend):
    """
    MailerSend API email backend using their REST API
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'MAILERSEND_API_KEY', None) or os.getenv('MAILERSEND_TOKEN')
        
    def send_messages(self, email_messages):
        """
        Send multiple email messages using MailerSend API
        """
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("MailerSend API key not configured")
            return 0
            
        try:
            import requests
        except ImportError:
            if not self.fail_silently:
                raise ImportError("Requests library not installed")
            logger.error("Requests library not installed")
            return 0
            
        sent_count = 0
        
        for message in email_messages:
            try:
                # Prepare MailerSend API payload
                payload = {
                    "from": {
                        "email": sanitize_address(message.from_email, message.encoding)[1],
                        "name": getattr(settings, 'DEFAULT_FROM_NAME', 'Buildly')
                    },
                    "to": [
                        {"email": sanitize_address(recipient, message.encoding)[1]}
                        for recipient in message.to
                    ],
                    "subject": message.subject,
                    "text": message.body if message.content_subtype == 'plain' else None,
                    "html": message.body if message.content_subtype == 'html' else None
                }
                
                # Handle HTML alternatives
                if hasattr(message, 'alternatives') and message.alternatives:
                    for alternative in message.alternatives:
                        if alternative[1] == 'text/html':
                            payload["html"] = alternative[0]
                
                # Remove None values
                payload = {k: v for k, v in payload.items() if v is not None}
                
                # Send API request
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                response = requests.post(
                    'https://api.mailersend.com/v1/email',
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    sent_count += len(message.to)
                    logger.info(f"Email sent successfully via MailerSend to {message.to}")
                else:
                    logger.error(f"MailerSend API error: {response.status_code} - {response.text}")
                    if not self.fail_silently:
                        raise Exception(f"MailerSend API error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Error sending email via MailerSend: {e}")
                if not self.fail_silently:
                    raise
                    
        return sent_count


class MailerSendSMTPBackend(EmailBackend):
    """
    Custom SMTP backend for MailerSend that handles their specific authentication format.
    MailerSend requires AUTH PLAIN with a specific format for token-based authentication.
    """

    def open(self):
        """
        Ensure a connection to the email server. Return whether or not a new
        connection was opened. Uses MailerSend-specific authentication.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        connection_params = {}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout
        if self.use_ssl:
            connection_params['context'] = self.ssl_context
        try:
            self.connection = smtplib.SMTP(
                self.host, self.port, **connection_params
            )

            # TLS/SSL are mutually exclusive, so only attempt TLS over
            # non-secure connections.
            if not self.use_ssl and self.use_tls:
                self.connection.starttls(context=self.ssl_context)
            
            if self.username and self.password:
                # Use MailerSend-specific AUTH PLAIN format
                # MailerSend expects the token in both username and password positions
                auth_string = base64.b64encode(
                    f'\x00{self.password}\x00{self.password}'.encode()
                ).decode()
                self.connection.docmd('AUTH PLAIN ' + auth_string)
            
            return True
        except OSError:
            if not self.fail_silently:
                raise
