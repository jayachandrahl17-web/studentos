from rest_framework.routers import DefaultRouter
from .views import SemesterViewSet,SubjectViewSet,ModuleViewSet,TopicViewSet
r=DefaultRouter(); r.register('semesters',SemesterViewSet); r.register('subjects',SubjectViewSet); r.register('modules',ModuleViewSet); r.register('topics',TopicViewSet)
urlpatterns=r.urls
