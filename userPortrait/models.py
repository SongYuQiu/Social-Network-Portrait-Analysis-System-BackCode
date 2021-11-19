from django.db import models


# Create your models here.
class UserPortrait(models.Model):
    id = models.AutoField(primary_key=True)
    weibo_user_id = models.CharField(max_length=32, blank=False, null=False, unique=True)
    # gender = models.CharField(max_length=32, blank=False, null=False)
    male_probability = models.FloatField(blank=True, null=True)
    female_probability = models.FloatField(blank=True, null=True)
    seven_probability = models.FloatField()
    eight_probability = models.FloatField()
    nine_probability = models.FloatField()
    interest = models.CharField(max_length=256, blank=False, null=False)
    portrait_date = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'weibo_user_id'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "UserPortrait"
        managed = True
