import os
import json
from pathlib import Path
from urllib.parse import urlsplit

from allianceauth.project_template.project_name.settings.base import *  # noqa: F403, F401

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ROOT_URLCONF = "local_auth.urls"
WSGI_APPLICATION = "local_auth.wsgi.application"
SECRET_KEY = os.getenv("AA_SECRET_KEY", "local-development-only-secret-key")

SITE_NAME = "Alliance Auth Development"
SITE_URL = os.getenv("AA_SITE_URL", "http://localhost:8000")
CSRF_TRUSTED_ORIGINS = [SITE_URL]
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "host.docker.internal", urlsplit(SITE_URL).hostname]
SESSION_COOKIE_SECURE = urlsplit(SITE_URL).scheme == "https"
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
DEBUG = True

STATIC_ROOT = Path("/data/static")

INSTALLED_APPS += [plugin["app"] for plugin in json.loads((PROJECT_ROOT.parent / "plugins.json").read_text())]  # noqa: F405
if "allianceauth_oidc" in INSTALLED_APPS:
    INSTALLED_APPS += ["oauth2_provider"]
    ALLIANCEAUTH_OIDC_EMAIL_DOMAIN = os.getenv("ALLIANCEAUTH_OIDC_EMAIL_DOMAIN", "test.com")
    OAUTH2_PROVIDER_APPLICATION_MODEL = "allianceauth_oidc.AllianceAuthApplication"
    OAUTH2_PROVIDER = {
        "OIDC_ENABLED": True,
        "OIDC_RSA_PRIVATE_KEY": Path("/run/secrets/oidc-private.pem").read_text(),
        "OAUTH2_VALIDATOR_CLASS": "allianceauth_oidc.auth_provider.AllianceAuthOAuth2Validator",
        "SCOPES": {
            "openid": "OpenID Connect",
            "email": "Email address",
            "profile": "Main character and Alliance Auth groups",
        },
        "PKCE_REQUIRED": False,
        "APPLICATION_ADMIN_CLASS": "allianceauth_oidc.admin.ApplicationAdmin",
    }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/data/alliance_auth.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("AA_REDIS_URL", "redis://redis:6379/1"),
    }
}

BROKER_URL = os.getenv("AA_REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = BROKER_URL
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

ESI_SSO_CLIENT_ID = os.getenv("AA_ESI_CLIENT_ID", "")
ESI_SSO_CLIENT_SECRET = os.getenv("AA_ESI_CLIENT_SECRET", "")
ESI_SSO_CALLBACK_URL = f"{SITE_URL}/sso/callback"
ESI_USER_CONTACT_EMAIL = os.getenv("AA_ESI_CONTACT_EMAIL", "developer@example.invalid")

REGISTRATION_VERIFY_EMAIL = False
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "allianceauth@example.invalid"

