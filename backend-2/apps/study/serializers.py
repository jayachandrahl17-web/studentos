from rest_framework import serializers
from .models import StudySession,Revision
class StudySessionSerializer(serializers.ModelSerializer):
    class Meta: model=StudySession; fields=('id','topic','minutes','studied_on','notes')
class RevisionSerializer(serializers.ModelSerializer):
    class Meta: model=Revision; fields=('id','topic','revised_on','confidence')
