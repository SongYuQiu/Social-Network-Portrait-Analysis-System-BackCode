# Generated by Django 2.2 on 2021-04-25 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weiboCrawler', '0017_remove_weibotext_weibo_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='weibotext',
            name='weibo_user_id',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
