from rest_framework import viewsets
from .models import QuizAttempt
from .serializers import QuizAttemptSerializer
class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset=QuizAttempt.objects.select_related('topic'); serializer_class=QuizAttemptSerializer
    def get_queryset(self): return super().get_queryset().filter(user=self.request.user)
    def perform_create(self,serializer): serializer.save(user=self.request.user)
