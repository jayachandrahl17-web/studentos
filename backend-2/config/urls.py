from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health(request):
    return JsonResponse({'status':'ok','service':'StudyOS API','version':'1.0'})

urlpatterns=[
    path('admin/',admin.site.urls),
    path('health/',health),
    path('api/accounts/',include('apps.accounts.urls')),
    path('api/academics/',include('apps.academics.urls')),
    path('api/resources/',include('apps.resources.urls')),
    path('api/study/',include('apps.study.urls')),
    path('api/assessments/',include('apps.assessments.urls')),
    path('api/quizzes/',include('apps.quizzes.urls')),
    path('api/questions/',include('apps.question_papers.urls')),
    path('api/analytics/',include('apps.analytics.urls')),
    path('api/ai/',include('apps.ai_engine.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
