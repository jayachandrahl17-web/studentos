from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from .models import StudySession,Revision
from .serializers import StudySessionSerializer,RevisionSerializer
class StudySessionViewSet(viewsets.ModelViewSet):
    queryset=StudySession.objects.select_related('topic__module__subject'); serializer_class=StudySessionSerializer
    def get_queryset(self): return super().get_queryset().filter(user=self.request.user)
    def perform_create(self,serializer): serializer.save(user=self.request.user)
class RevisionViewSet(viewsets.ModelViewSet):
    queryset=Revision.objects.select_related('topic'); serializer_class=RevisionSerializer
    def get_queryset(self): return super().get_queryset().filter(user=self.request.user)
    def perform_create(self,serializer): serializer.save(user=self.request.user)
@api_view(['GET'])
def today(request):
    qs=StudySession.objects.filter(user=request.user,studied_on__date=timezone.localdate()); return Response({'date':timezone.localdate(),'minutes':qs.aggregate(total=Sum('minutes'))['total'] or 0,'sessions':StudySessionSerializer(qs,many=True).data})
