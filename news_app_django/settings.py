"""
Django settings for news_app_django project.

Generated by 'django-admin startproject' using Django 5.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 環境変数ファイルの読み込み
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-a!8ek8t#@^spi^3l@atk9!&qu7!#&%07j67m+auo9vd@juc$s2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "news_app.apps.NewsAppConfig",
    "accounts.apps.AccountsConfig",

    "django.contrib.sites",
    "allauth",
    "allauth.account",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "news_app_django.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "news_app_django.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "news_app",
        "USER": os.getenv("DB_USER"), 
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": "",
        "PORT": "",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ja"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ロギング設定
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # ロガーの設定
    "loggers": {
        # Djangoが利用するロガー
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        # news_appアプリケーションが利用するロガー
        "news_app": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },

    # ハンドラの設定
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "dev",
        },
    },

    # フォーマッタの設定
    "formatters": {
        "dev": {
            "format": "\t".join([
                "%(asctime)s",
                "[%(levelname)s]",
                "%(pathname)s(Line:%(lineno)d)",
                "%(message)s"
            ])
        },
    },
}

# ユーザーモデルの設定
AUTH_USER_MODEL = "accounts.CustomUser"

# django-allauthの設定
SITE_ID = 1

# 認証バックエンドの設定（Django + Allauth）
AUTHENTICATION_BACKENDS = [
    # Djangoのデフォルト認証バックエンド
    'django.contrib.auth.backends.ModelBackend',

    # allauthの認証バックエンド
    'allauth.account.auth_backends.AuthenticationBackend',
]

# allauthの設定（ユーザー名 + パスワードのみで認証するためのもの）
ACCOUNT_LOGIN_METHODS = {"username"}     # ユーザー名でログイン
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']  # ユーザー名とパスワードのみでサインアップ
ACCOUNT_EMAIL_VERIFICATION = "none"            # メール認証なし
ACCOUNT_LOGIN_ON_SIGNUP = True                 # サインアップ後に即ログイン
LOGIN_REDIRECT_URL = "news_app:index"              # ログイン後のリダイレクト先
ACCOUNT_LOGOUT_REDIRECT_URL = "news_app:index"      # ログアウト後のリダイレクト先

# staticファイル読み込み
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
