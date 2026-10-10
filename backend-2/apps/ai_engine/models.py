from django.db import models
from django.conf import settings
class AIInteraction(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='ai_interactions',null=True,blank=True)
    question=models.TextField()
    answer=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
class PredictionRun(models.Model):
    subject=models.ForeignKey('academics.Subject',on_delete=models.CASCADE,null=True,blank=True)
    model_name=models.CharField(max_length=100)
    prediction=models.FloatField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
