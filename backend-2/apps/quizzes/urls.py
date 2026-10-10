from rest_framework.routers import DefaultRouter
from .views import QuizAttemptViewSet
r=DefaultRouter(); r.register('attempts',QuizAttemptViewSet); urlpatterns=r.urls
