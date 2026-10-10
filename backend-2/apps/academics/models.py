from django.db import models
from django.conf import settings

class Semester(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100, default='Semester')
    academic_year = models.CharField(max_length=20, default='2026-27')

    # Semester timeline
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Internal assessments
    cia1_start_date = models.DateField(null=True, blank=True)
    cia1_end_date = models.DateField(null=True, blank=True)

    cia2_start_date = models.DateField(null=True, blank=True)
    cia2_end_date = models.DateField(null=True, blank=True)

    # Semester-end examination
    see_start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Semester {self.number}'

class Subject(models.Model):
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE,related_name='subjects')
    name=models.CharField(max_length=200)
    code=models.CharField(max_length=30,unique=True)
    credits=models.PositiveIntegerField(default=3)
    is_lab=models.BooleanField(default=False)
    color=models.CharField(max_length=30,default='indigo')
    class Meta: ordering=['name']
    def __str__(self): return f'{self.code} - {self.name}'

class Module(models.Model):
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='modules')
    number=models.PositiveIntegerField()
    name=models.CharField(max_length=250)
    estimated_minutes=models.PositiveIntegerField(default=180)
    class Meta:
        ordering=['subject','number']; constraints=[models.UniqueConstraint(fields=['subject','number'],name='unique_module_number_per_subject')]
    def __str__(self): return f'{self.subject.code} M{self.number}: {self.name}'

class Topic(models.Model):
    module=models.ForeignKey(Module,on_delete=models.CASCADE,related_name='topics')
    name=models.CharField(max_length=300)
    estimated_minutes=models.PositiveIntegerField(default=30)
    importance=models.PositiveIntegerField(default=3) # 1-5
    class Meta: ordering=['module','id']
    def __str__(self): return self.name

class TopicProgress(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='topic_progress')
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE,related_name='progress_records')
    completed=models.BooleanField(default=False)
    mastery=models.FloatField(default=0.0)
    last_studied=models.DateTimeField(null=True,blank=True)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['user','topic'],name='unique_user_topic_progress')]

    def __str__(self): return f'{self.user} - {self.topic}'
