from django.db import models
from apps.academics.models import Topic,Subject
class QuestionPaper(models.Model):
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='question_papers')
    year=models.PositiveIntegerField()
    title=models.CharField(max_length=200,blank=True)
    file=models.FileField(upload_to='question_papers/',blank=True,null=True)
class Question(models.Model):
    paper=models.ForeignKey(QuestionPaper,on_delete=models.CASCADE,related_name='questions')
    text=models.TextField()
    marks=models.PositiveIntegerField(default=2)
    topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True,blank=True,related_name='past_questions')
    frequency=models.PositiveIntegerField(default=1)
