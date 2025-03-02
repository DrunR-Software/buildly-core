from .base import *

MIDDLEWARE_AUTHENTICATION = [
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

MIDDLEWARE = MIDDLEWARE_DJANGO + MIDDLEWARE_AUTHENTICATION

# Authentication backends
# https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-AUTHENTICATION_BACKENDS

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
]

# Auth Application
OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', None)
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', None)

# JWT Authentication settings
JWT_PAYLOAD_ENRICHER = 'core.jwt_utils.payload_enricher'
JWT_ISSUER = os.getenv('JWT_ISSUER', '')
JWT_ALLOWED_ISSUER = os.getenv('JWT_ISSUER', '')
JWT_AUTH_DISABLED = False
JWT_PRIVATE_KEY_RSA_BUILDLY = os.getenv('JWT_PRIVATE_KEY_RSA_BUILDLY', '').replace('\\n', '\n')
JWT_PUBLIC_KEY_RSA_BUILDLY = os.getenv('JWT_PUBLIC_KEY_RSA_BUILDLY', '').replace('\\n', '\n')

# Password Validators
AUTH_PASSWORD_VALIDATORS = []

AUTH_PASSWORD_VALIDATORS_MAP = {
    'USE_PASSWORD_USER_ATTRIBUTE_SIMILARITY_VALIDATOR': {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    'USE_PASSWORD_MINIMUM_LENGTH_VALIDATOR': {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': int(os.getenv('PASSWORD_MINIMUM_LENGTH', 6))},
    },
    'USE_PASSWORD_COMMON_VALIDATOR': {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    'USE_PASSWORD_NUMERIC_VALIDATOR': {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
}

for (
    password_validator_env_var,
    password_validator,
) in AUTH_PASSWORD_VALIDATORS_MAP.items():
    if os.getenv(password_validator_env_var, 'True') == 'True':
        AUTH_PASSWORD_VALIDATORS.append(password_validator)

# Social Auth
LOGIN_URL = os.getenv('LOGIN_URL', FRONTEND_URL)
LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SOCIAL_AUTH_REDIRECT_IS_HTTPS = (
    True if os.getenv('SOCIAL_AUTH_REDIRECT_IS_HTTPS') == 'True' else False
)
SOCIAL_AUTH_LOGIN_REDIRECT_URLS = {
    'github': os.getenv('SOCIAL_AUTH_GITHUB_REDIRECT_URL', None),
    'google-oauth2': os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URL', None),
    'microsoft-graph': os.getenv('SOCIAL_AUTH_MICROSOFT_GRAPH_REDIRECT_URL', None),
}

SOCIAL_AUTH_PIPELINE = (
    'core.auth_pipeline.create_organization',
)

# Github social auth
SOCIAL_AUTH_GITHUB_KEY = os.getenv('SOCIAL_AUTH_GITHUB_KEY', '')
SOCIAL_AUTH_GITHUB_SECRET = os.getenv('SOCIAL_AUTH_GITHUB_SECRET', '')
SOCIAL_AUTH_GITHUB_SCOPE = ['email']

# Google social auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')

# Microsoft social auth
SOCIAL_AUTH_MICROSOFT_GRAPH_KEY = os.getenv('SOCIAL_AUTH_MICROSOFT_GRAPH_KEY', '')
SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET = os.getenv('SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET', '')


# Whitelist of domains allowed to login via social auths
# i.e. ['example.com', 'buildly.io','treeaid.org']
if os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS'):
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = os.getenv(
        'SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS').split(',')
if os.getenv('SOCIAL_AUTH_MICROSOFT_WHITELISTED_DOMAINS'):
    SOCIAL_AUTH_GOOGLE_MICROSOFT_DOMAINS = os.getenv(
        'SOCIAL_AUTH_MICROSOFT_WHITELISTED_DOMAINS'
    ).split(',')

# oauth2 settings
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS', 36000)),
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'introspection': 'Introspect token scope',
    },
}

DEFAULT_OAUTH_DOMAINS = os.getenv('DEFAULT_OAUTH_DOMAINS', '')
CREATE_DEFAULT_PROGRAM = (
    True if os.getenv('CREATE_DEFAULT_PROGRAM') == 'True' else False
)