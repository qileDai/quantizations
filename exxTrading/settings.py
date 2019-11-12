"""
Django settings for exxTrading project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from exxTrading import configuration


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5xr53c^_f)d%ug(zs39l!(si^18=dh623uwhk87e^fzwp@4233'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['*']  # 允许所有ip访问
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = ('*')




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'apps.rbac',
    'apps.deal',
    'django_crontab',       # 定时任务
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # 跨域
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'apps.rbac.middleware.rbac.RbacMiddleware',  # 加入自定义的中间件到最后

]

ROOT_URLCONF = 'exxTrading.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'front', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'exxTrading.wsgi.application'
# token失效时间，设置为1天，开发可自行配置
AUTH_TOKEN_AGE = 60 * 60 * 24
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
import pymysql
pymysql.install_as_MySQLdb()
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'exx_quantitvate_streagety',
#         'HOST': '192.168.4.201',
#         'PORT': 3306,
#         'USER': 'root',
#         'PASSWORD': 'password'
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': configuration.ENGINE,
        'NAME': configuration.NAME,
        'HOST': configuration.HOST,
        'PORT': 3306,
        'USER': configuration.USER,
        'PASSWORD': configuration.PASSWORD
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://" + configuration.REDIS_HOST,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "PASSWORD": configuration.REDIS_PWD,
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'


TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# AUTH_USER_MODEL = 'user.UserProfile'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'front', 'dist')
]

# 定义session 键：

# 保存用户权限url列表
SESSION_PERMISSION_URL_KEY = 'url_list'
# 保存 权限菜单 和所有 菜单
SESSION_MENU_KEY = 'menu_list'
ALL_MENU_KEY = 'all_menu'
PERMISSION_MENU_KEY = 'permission_menu'

LOGIN_URL = '/login/'

# url作严格匹配
REGEX_URL = r'^{url}$'

# 配置url权限白名单
SAFE_URL = [
    r'',
    r'/login/',
    '/admin/.*',
    '/test/',
    '/rbac/index/',
    '^/rbac/',
    r'/exx/',
    '/deal/',
    '/docs/',
]

# 用户是否登陆
LOGIN = 'is_login'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # LimitOffsetPagination 分页风格
    'PAGE_SIZE': 20,  # 每页多少条记录
}

# # redis配置
# REDIS_HOST = '192.168.4.179'
# REDIS_PWD = 'sHZQ4zLB6LasF8ox'


# 分钟(0-59) 小时(0-23) 每个月的哪一天(1-31) 月份(1-12) 周几(0-6) shell脚本或者命令
CRONJOBS = [
    ('*/30 * * * *', 'apps.deal.cron.exx_scheduled_job', '>>/home/lee.log'),
]

# 跨域
CORS_ORIGIN_ALLOW_ALL = True  # 允许所有的请求，或者设置CORS_ORIGIN_WHITELIST，二选一
CORS_ALLOW_HEADERS = ('*')  # 允许所有的请求头
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie，前端需要携带cookies访问后端时,需要设置withCredentials: true







