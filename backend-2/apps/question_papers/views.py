from rest_framework import viewsets
from .models import QuestionPaper,Question
from .serializers import QuestionPaperSerializer,QuestionSerializer
class QuestionPaperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=QuestionPaper.objects.select_related('subject').prefetch_related('questions'); serializer_class=QuestionPaperSerializer
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Question.objects.select_related('paper','topic'); serializer_class=QuestionSerializer
