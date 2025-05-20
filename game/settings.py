AUTH_USER_MODEL = "game.CustomUser"
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
INSTALLED_APPS = [
    # ...
    'django.contrib.admin',
    'django.contrib.auth',   # Must be present
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ...
    'game',  # your app
]
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
