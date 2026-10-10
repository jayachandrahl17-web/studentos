from django.db import models
from django.conf import settings
class DailySnapshot(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='daily_snapshots',null=True,blank=True)
    date=models.DateField()
    minutes=models.PositiveIntegerField(default=0)
    topics_completed=models.PositiveIntegerField(default=0)
    quiz_accuracy=models.FloatField(default=0)
    created_at=models.DateTimeField(auto_now=True)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['user','date'],name='unique_user_snapshot_date')]
