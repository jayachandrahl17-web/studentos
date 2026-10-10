from django.urls import path
from .views import overview,dashboard
urlpatterns=[path('overview/',overview),path('dashboard/',dashboard)]
