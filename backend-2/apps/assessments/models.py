from django.db import models
from django.conf import settings
from apps.academics.models import Subject
class Assessment(models.Model):
    TYPES=[('internal_1','Internal 1'),('internal_2','Internal 2'),('semester','Semester Exam'),('lab','Lab Exam')]
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='assessments')
    name=models.CharField(max_length=150)
    assessment_type=models.CharField(max_length=30,choices=TYPES,default='internal_1')
    date=models.DateField()
    max_marks=models.PositiveIntegerField(default=50)
    weight=models.FloatField(default=1.0)
    syllabus_modules=models.PositiveIntegerField(default=2)
    def __str__(self): return f'{self.name} - {self.subject.code}'
class Mark(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='marks',null=True,blank=True)
    assessment=models.ForeignKey(Assessment,on_delete=models.CASCADE,related_name='marks')
    score=models.FloatField()
    note=models.TextField(blank=True)
    recorded_at=models.DateTimeField(auto_now_add=True)
