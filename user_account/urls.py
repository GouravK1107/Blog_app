from django.urls import path, include
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.custom_logout_view, name='logout'),
    path("accounts/", include("allauth.urls")),
]