# Generated by Django 2.2.19 on 2021-04-13 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weiboCrawler', '0006_auto_20210413_1203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weibouser',
            name='registration_date',
        ),
    ]
