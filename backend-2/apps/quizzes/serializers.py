from rest_framework import serializers
from .models import QuizAttempt
class QuizAttemptSerializer(serializers.ModelSerializer):
    accuracy=serializers.ReadOnlyField()
    class Meta: model=QuizAttempt; fields=('id','topic','questions','correct','attempted_on','accuracy')
