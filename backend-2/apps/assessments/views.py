from rest_framework import viewsets
from .models import Assessment,Mark
from .serializers import AssessmentSerializer,MarkSerializer
class AssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Assessment.objects.select_related('subject').prefetch_related('marks'); serializer_class=AssessmentSerializer
    def get_queryset(self):
        qs=super().get_queryset(); subject=self.request.query_params.get('subject'); return qs.filter(subject_id=subject) if subject else qs
class MarkViewSet(viewsets.ModelViewSet):
    queryset=Mark.objects.select_related('assessment__subject'); serializer_class=MarkSerializer
    def get_queryset(self): return super().get_queryset().filter(user=self.request.user)
    def perform_create(self,serializer): serializer.save(user=self.request.user)
