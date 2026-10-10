from django.db import models
from apps.academics.models import Topic
class Resource(models.Model):
    TYPES=[('pdf','PDF'),('notes','Notes'),('video','Video'),('link','Link'),('book','Book')]
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE,related_name='resources',null=True,blank=True)
    title=models.CharField(max_length=250)
    url=models.URLField(blank=True)
    resource_type=models.CharField(max_length=20,choices=TYPES,default='link')
    uploaded_file=models.FileField(upload_to='resources/',blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title
