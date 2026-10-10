from django.urls import path
from .views import overview, mastery, risk, study_plan, prediction, chat_api, target, classify_question

urlpatterns = [
    path('overview/', overview),
    path('mastery/', mastery),
    path('risk/', risk),
    path('study-plan/', study_plan),
    path('prediction/', prediction),
    path('chat/', chat_api),
    path('target/', target),
    path('classify-question/', classify_question),
]
