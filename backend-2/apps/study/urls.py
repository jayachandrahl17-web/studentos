from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import StudySessionViewSet,RevisionViewSet,today
r=DefaultRouter(); r.register('sessions',StudySessionViewSet); r.register('revisions',RevisionViewSet)
urlpatterns=r.urls+[path('today/',today)]
