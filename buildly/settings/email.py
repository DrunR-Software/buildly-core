from .base import *

# Email configuration based on EMAIL_SERVICE environment variable

EMAIL_SERVICE = os.getenv('EMAIL_SERVICE', 'SENDGRID')

if EMAIL_SERVICE == 'MAILERSEND':
    # MailerSend SMTP Configuration
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.mailersend.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('MAILERSEND_SMTP_USERNAME')
    EMAIL_HOST_PASSWORD = os.getenv('MAILERSEND_SMTP_PASSWORD')
    
    # Alternative: MailerSend API Backend (if you prefer API over SMTP)
    # EMAIL_BACKEND = 'core.email_backends.MailerSendAPIBackend'
    # MAILERSEND_API_KEY = os.getenv('MAILERSEND_TOKEN')
    
elif EMAIL_SERVICE == 'SENDGRID':
    # SendGrid SMTP Configuration
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'  # Always 'apikey' for SendGrid
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # SendGrid API key
    
    # Alternative: SendGrid API Backend (if you prefer API over SMTP)
    # EMAIL_BACKEND = 'core.email_backends.SendGridAPIBackend'
    # SENDGRID_API_KEY = os.getenv('EMAIL_HOST_PASSWORD')
    
elif os.getenv('EMAIL_BACKEND') == 'SMTP':
    # Custom SMTP Configuration (fallback)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
else:
    # Development/Testing - use in-memory backend
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Common email settings
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
DEFAULT_REPLYTO_EMAIL = os.getenv('DEFAULT_REPLYTO_EMAIL')
RESETPASS_CONFIRM_URL_PATH = os.getenv('RESETPASS_CONFIRM_URL_PATH')
