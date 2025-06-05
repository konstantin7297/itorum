from django.urls import path

from . import views

urlpatterns = [
    path('user/register/', views.RegisterView.as_view(), name="register"),
    path('user/login/', views.LoginView.as_view(), name="login"),
    path('user/logout/', views.LogoutView.as_view(), name="logout"),
]
