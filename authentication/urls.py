from django.urls import path,include
from authentication.views import *

urlpatterns = [
    path('login', loginView, name='Login'),
    path('register', registerView, name='Register'),
    path('logout', logoutView, name='logout'),
] 