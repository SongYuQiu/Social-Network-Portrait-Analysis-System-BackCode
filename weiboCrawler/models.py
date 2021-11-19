from django.db import models


# Create your models here.
class WeiboUser(models.Model):
    id = models.AutoField(primary_key=True)
    weibo_user_id = models.CharField(max_length=32, blank=False, null=False, unique=True)
    screen_name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    gender = models.CharField(max_length=32, blank=False)
    location = models.CharField(max_length=256, blank=True, null=True)
    statuses_count = models.IntegerField()
    followers_count = models.IntegerField()
    follow_count = models.IntegerField()
    description = models.CharField(max_length=256, null=True, blank=True)
    avatar_hd = models.CharField(max_length=256)
    profile_url = models.CharField(max_length=256, blank=True, null=True)
    weibo_rank = models.IntegerField()
    member_rank = models.IntegerField()
    verified = models.BooleanField(default=False)
    verified_reason = models.CharField(max_length=256, null=True, blank=True)
    since_date = models.DateTimeField(blank=True, null=True)
    last_date = models.DateTimeField(blank=True, null=True)
    portrait_status = models.BooleanField(default=False)

    USERNAME_FIELD = 'weibo_user_id'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "WeiboUser"
        managed = True


class WeiboText(models.Model):
    id = models.AutoField(primary_key=True)
    weibo_text_id = models.CharField(max_length=32, unique=True)
    weibo_user_id = models.CharField(max_length=32, blank=True, null=True)
    text = models.TextField()
    topic = models.CharField(max_length=128)
    location = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField()
    tool = models.CharField(max_length=64)
    like_count = models.IntegerField()
    comment_count = models.IntegerField()
    repost_count = models.IntegerField()

    class Meta:
        db_table = "WeiboText"
