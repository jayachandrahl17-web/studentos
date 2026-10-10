from rest_framework import serializers
from .models import Assessment,Mark
class MarkSerializer(serializers.ModelSerializer):
    class Meta: model=Mark; fields=('id','assessment','score','note','recorded_at')
    def validate(self,attrs):
        assessment=attrs.get('assessment',getattr(self.instance,'assessment',None))
        score=attrs.get('score',getattr(self.instance,'score',None))
        if score is not None and (score < 0 or score > assessment.max_marks):
            raise serializers.ValidationError({'score':f'Score must be between 0 and {assessment.max_marks}.'})
        return attrs
class AssessmentSerializer(serializers.ModelSerializer):
    marks=serializers.SerializerMethodField()
    days_left=serializers.SerializerMethodField()
    subject_name=serializers.CharField(source='subject.name',read_only=True)
    class Meta: model=Assessment; fields='__all__'
    def get_marks(self,obj):
        request=self.context.get('request')
        marks=obj.marks.filter(user=request.user) if request and request.user.is_authenticated else obj.marks.none()
        return MarkSerializer(marks,many=True,context=self.context).data
    def get_days_left(self,obj):
        from django.utils import timezone
        return max(0,(obj.date-timezone.localdate()).days)
