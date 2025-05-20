from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

class MyLogoutView(LogoutView):
    http_method_names = ['get', 'post']

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('accounts/logout/', LogoutView.as_view(), name='logout'),  
    path('', include('game.urls')),
    #path('accounts/profile/', profile_view, name='profile'),
]

