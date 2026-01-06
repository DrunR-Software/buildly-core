import logging
from smtplib import SMTPException
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(
    email_address: str,
    subject: str,
    context: dict,
    template_name: str,
    html_template_name: str = None,
) -> int:
    try:
        logger.info(f"Rendering email templates for {email_address}")
        logger.debug(f"Text template: {template_name}")
        logger.debug(f"HTML template: {html_template_name}")
        logger.debug(f"Context keys: {list(context.keys())}")
        
        text_content = loader.render_to_string(template_name, context, using=None)
        logger.debug(f"Text template rendered successfully ({len(text_content)} chars)")
        
        html_content = (
            loader.render_to_string(html_template_name, context, using=None)
            if html_template_name
            else None
        )
        if html_content:
            logger.debug(f"HTML template rendered successfully ({len(html_content)} chars)")
        
        return send_email_body(email_address, subject, text_content, html_content)
    except Exception as e:
        logger.error(f"Failed to render email templates for {email_address}: {str(e)}")
        logger.error(f"Template details - Text: {template_name}, HTML: {html_template_name}")
        raise


def send_email_body(
    email_address: str, subject: str, text_content: str, html_content: str = None
) -> int:
    try:
        logger.info(f"Preparing email to {email_address} with subject: {subject}")
        logger.debug(f"Email backend configured: {settings.EMAIL_BACKEND}")
        logger.debug(f"Email host: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
        logger.debug(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        
        msg = EmailMultiAlternatives(
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject=subject,
            body=text_content,
            to=[email_address],
        )
        
        if settings.DEFAULT_REPLYTO_EMAIL:
            msg.reply_to = [settings.DEFAULT_REPLYTO_EMAIL]
            logger.debug(f"Reply-to set: {settings.DEFAULT_REPLYTO_EMAIL}")
            
        if html_content:
            msg.attach_alternative(html_content, "text/html")
            logger.debug("HTML alternative attached")
        
        logger.info(f"Sending email via Django backend...")
        result = msg.send()
        logger.info(f"Email sent successfully to {email_address}: {subject} (result: {result})")
        return result
    except SMTPException as e:
        logger.error(f"SMTP error sending email to {email_address}: {str(e)}")
        logger.error(f"SMTP error details - Host: {getattr(settings, 'EMAIL_HOST', 'Unknown')}, Port: {getattr(settings, 'EMAIL_PORT', 'Unknown')}")
        raise
    except (ConnectionError, TimeoutError) as e:
        logger.error(f"Connection error sending email to {email_address}: {str(e)}")
        logger.error(f"Connection details - Host: {getattr(settings, 'EMAIL_HOST', 'Unknown')}, Timeout occurred")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending email to {email_address}: {str(e)}")
        logger.error(f"Email configuration - Backend: {settings.EMAIL_BACKEND}")
        raise
