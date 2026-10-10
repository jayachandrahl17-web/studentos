from rest_framework.routers import DefaultRouter
from .views import QuestionPaperViewSet,QuestionViewSet
r=DefaultRouter(); r.register('papers',QuestionPaperViewSet); r.register('questions',QuestionViewSet); urlpatterns=r.urls
