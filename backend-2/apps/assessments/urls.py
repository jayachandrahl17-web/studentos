from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet,MarkViewSet
r=DefaultRouter(); r.register('assessments',AssessmentViewSet); r.register('marks',MarkViewSet); urlpatterns=r.urls
