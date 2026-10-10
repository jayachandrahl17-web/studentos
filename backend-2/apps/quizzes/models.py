from django.db import models
from django.conf import settings
from apps.academics.models import Topic
class QuizAttempt(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='quiz_attempts',null=True,blank=True)
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE,related_name='quiz_attempts')
    questions=models.PositiveIntegerField()
    correct=models.PositiveIntegerField()
    attempted_on=models.DateTimeField(auto_now_add=True)
    @property
    def accuracy(self): return round((self.correct/self.questions)*100,2) if self.questions else 0
