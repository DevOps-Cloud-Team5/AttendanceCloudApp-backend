import os, datetime
from decouple import config



DEBUG = True

USE_TZ = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USE_I18N = True

USE_L10N = True

DATABASES = {
	'default': {
		'HOST': config('DB_HOST'),
		'NAME': config('DB_NAME'),
		'PORT': config('DB_PORT'),
		'USER': config('DB_USER'),
		'ENGINE': "django.db.backends.postgresql_psycopg2",
		'PASSWORD': config('DB_PASSWORD'),
	}
}

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			]
		}
	}
]

TIME_ZONE = 'UTC'

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'AUTH_HEADER_TYPES': ('JWT',),
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

STATIC_URL = '/static/'

ROOT_URLCONF = 'api.urls'

ALLOWED_HOSTS = ['*']

LANGUAGE_CODE = 'en-us'

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'corsheaders',
	'rest_framework',
 	"api.apps.ApiConfig"
]

AUTH_USER_MODEL = "api.User"

WSGI_APPLICATION = 'api.wsgi.application'

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')

CORS_ALLOW_HEADERS = [
	'x-requested-with',
	'content-type',
	'accept',
	'origin',
	'authorization',
	'accept-encoding',
	'x-csrftoken',
	'access-control-allow-origin',
	'content-disposition',
]

CORS_ALLOW_METHODS = [
	'GET',
	'POST',
	'PUT',
	'PATCH',
	'DELETE',
	'OPTIONS',
]

AWS_S3_CUSTOM_DOMAIN = f'{config("AWS_STORAGE_BUCKET_NAME")}.s3.amazonaws.com'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = False

AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')

AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(minutes=30),
    'ROTATE_REFRESH_TOKENS': True,
    
	'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'AUTH_HEADER_TYPES': ('JWT',),
}