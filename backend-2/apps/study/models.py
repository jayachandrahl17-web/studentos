from django.db import models
from django.conf import settings
from apps.academics.models import Topic
class StudySession(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='study_sessions',null=True,blank=True)
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE,related_name='study_sessions')
    minutes=models.PositiveIntegerField()
    studied_on=models.DateTimeField(auto_now_add=True)
    notes=models.TextField(blank=True)
    def __str__(self): return f'{self.topic.name} - {self.minutes} min'
class Revision(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='revisions',null=True,blank=True)
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE,related_name='revisions')
    revised_on=models.DateTimeField(auto_now_add=True)
    confidence=models.PositiveIntegerField(default=3)
