from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet
r=DefaultRouter(); r.register('resources',ResourceViewSet); urlpatterns=r.urls
