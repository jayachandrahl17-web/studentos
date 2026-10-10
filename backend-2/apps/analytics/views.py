from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg,Sum
from django.utils import timezone
from datetime import timedelta
from apps.academics.models import Subject,TopicProgress
from apps.study.models import StudySession
from apps.quizzes.models import QuizAttempt
from apps.assessments.models import Assessment
from apps.academics.serializers import SubjectSerializer
from apps.assessments.serializers import AssessmentSerializer
from apps.ai_engine.services import build_plan,sync_mastery

@api_view(['GET'])
def dashboard(request):
  return Response(dashboard_data(request))


def dashboard_data(request):
    sync_mastery(request.user)
    now=timezone.localdate()
    start=timezone.now()-timedelta(days=7)
    sessions=StudySession.objects.filter(user=request.user,studied_on__gte=start)
    attempts=QuizAttempt.objects.filter(user=request.user,attempted_on__gte=start)
    total_q=sum(x.questions for x in attempts); total_c=sum(x.correct for x in attempts)
    subjects=Subject.objects.select_related('semester').prefetch_related('modules__topics')
    upcoming=Assessment.objects.filter(date__gte=now).select_related('subject').order_by('date')[:6]
    mastery=TopicProgress.objects.filter(user=request.user).aggregate(value=Avg('mastery'))['value'] or 0
    return {
      'subjects':SubjectSerializer(subjects,many=True,context={'request':request}).data,
      'upcoming_assessments':AssessmentSerializer(upcoming,many=True,context={'request':request}).data,
      'study_minutes_week':sessions.aggregate(x=Sum('minutes'))['x'] or 0,
      'quiz_accuracy_week':round(total_c/total_q*100,1) if total_q else 0,
      'topic_mastery':round(mastery,1),
      'plan':build_plan(120,user=request.user),
    }

@api_view(['GET'])
def overview(request):
    data=dashboard_data(request)
    return Response({'study_minutes':data['study_minutes_week'],'quiz_accuracy':data['quiz_accuracy_week'],'topic_mastery':data['topic_mastery'],'subjects':len(data['subjects'])})
