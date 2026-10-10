from rest_framework import serializers
from .models import AIInteraction,PredictionRun
class AIInteractionSerializer(serializers.ModelSerializer):
    class Meta: model=AIInteraction; fields='__all__'
class PredictionRunSerializer(serializers.ModelSerializer):
    class Meta: model=PredictionRun; fields='__all__'
