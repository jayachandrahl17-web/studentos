from rest_framework import viewsets
from .models import Resource
from .serializers import ResourceSerializer
class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Resource.objects.all(); serializer_class=ResourceSerializer
    def get_queryset(self):
        qs=super().get_queryset(); topic=self.request.query_params.get('topic'); return qs.filter(topic_id=topic) if topic else qs
