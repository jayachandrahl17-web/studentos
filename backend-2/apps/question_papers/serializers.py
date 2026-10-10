from rest_framework import serializers
from .models import QuestionPaper,Question
class QuestionSerializer(serializers.ModelSerializer):
    class Meta: model=Question; fields='__all__'
class QuestionPaperSerializer(serializers.ModelSerializer):
    questions=QuestionSerializer(many=True,read_only=True)
    class Meta: model=QuestionPaper; fields='__all__'
