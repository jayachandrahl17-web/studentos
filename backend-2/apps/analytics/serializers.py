from rest_framework import serializers
from .models import DailySnapshot
class DailySnapshotSerializer(serializers.ModelSerializer):
    class Meta: model=DailySnapshot; fields='__all__'
