from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('register$', views.register, name='register'),
    url('home$', views.home, name='home'),
    url('login$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url('logout$', views.logout_view, name='logout')
]