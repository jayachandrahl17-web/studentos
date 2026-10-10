from rest_framework import serializers
from .models import Semester,Subject,Module,Topic,TopicProgress


class SemesterSerializer(serializers.ModelSerializer):
    class Meta: model=Semester; fields='__all__'


class SubjectSerializer(serializers.ModelSerializer):
    semester_name=serializers.CharField(source='semester.name',read_only=True)
    progress=serializers.SerializerMethodField()
    module_count=serializers.SerializerMethodField()
    topic_count=serializers.SerializerMethodField()
    class Meta: model=Subject; fields=('id','semester','semester_name','name','code','credits','is_lab','color','progress','module_count','topic_count')
    def get_progress(self,obj):
        user=self.context.get('request').user if self.context.get('request') else None
        total=Topic.objects.filter(module__subject=obj).count()
        done=TopicProgress.objects.filter(user=user,topic__module__subject=obj,completed=True).count() if user and user.is_authenticated else 0
        return round(done/total*100) if total else 0
    def get_module_count(self,obj): return obj.modules.count()
    def get_topic_count(self,obj): return sum(m.topics.count() for m in obj.modules.all())


class ModuleSerializer(serializers.ModelSerializer):
    progress=serializers.SerializerMethodField()
    topic_count=serializers.SerializerMethodField()
    completed_topics=serializers.SerializerMethodField()
    class Meta: model=Module; fields=('id','subject','number','name','estimated_minutes','progress','topic_count','completed_topics')
    def get_completed_topics(self,obj):
        user=self.context.get('request').user if self.context.get('request') else None
        return TopicProgress.objects.filter(user=user,topic__module=obj,completed=True).count() if user and user.is_authenticated else 0
    def get_progress(self,obj):
        total=obj.topics.count(); done=self.get_completed_topics(obj)
        return round(done/total*100) if total else 0
    def get_topic_count(self,obj): return obj.topics.count()


class TopicSerializer(serializers.ModelSerializer):
    subject=serializers.CharField(source='module.subject.name',read_only=True)
    module_number=serializers.IntegerField(source='module.number',read_only=True)
    completed=serializers.SerializerMethodField()
    mastery=serializers.SerializerMethodField()
    last_studied=serializers.SerializerMethodField()
    quiz_accuracy=serializers.SerializerMethodField()
    question_frequency=serializers.SerializerMethodField()
    class Meta: model=Topic; fields=('id','module','name','estimated_minutes','importance','subject','module_number','completed','mastery','last_studied','quiz_accuracy','question_frequency')
    def get_progress(self,obj):
        request=self.context.get('request')
        if not request or not request.user.is_authenticated: return None
        return TopicProgress.objects.filter(user=request.user,topic=obj).first()
    def get_completed(self,obj):
        progress=self.get_progress(obj)
        return progress.completed if progress else False
    def get_mastery(self,obj):
        progress=self.get_progress(obj)
        return progress.mastery if progress else 0.0
    def get_last_studied(self,obj):
        progress=self.get_progress(obj)
        return progress.last_studied if progress else None
    def get_question_frequency(self,obj): return obj.past_questions.count()
    def get_quiz_accuracy(self,obj):
        request=self.context.get('request')
        attempts=obj.quiz_attempts.filter(user=request.user) if request and request.user.is_authenticated else obj.quiz_attempts.none()
        q=sum(a.questions for a in attempts); c=sum(a.correct for a in attempts); return round(c/q*100,1) if q else 0
