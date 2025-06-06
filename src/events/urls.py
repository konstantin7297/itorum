from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.EventView)

urlpatterns = [
    path('', include(router.urls)),
    # path('', views.a.as_view(), name='all-events'),
    # path('<int:pk>/', views.a.as_view(), name='event'),
    # path('booking/', views.a.as_view(), name='booking'),
    # path('user/<int:pk>/', views.a.as_view(), name='user-events'),
]
