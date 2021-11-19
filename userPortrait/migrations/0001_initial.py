# Generated by Django 2.2 on 2021-04-29 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserPortrait',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('weibo_user_id', models.CharField(max_length=32, unique=True)),
                ('gender', models.CharField(max_length=32)),
                ('gender_probability', models.FloatField()),
                ('seven_probability', models.FloatField()),
                ('eight_probability', models.FloatField()),
                ('nine_probability', models.FloatField()),
                ('interest', models.CharField(max_length=256)),
                ('portrait_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'UserPortrait',
                'managed': True,
            },
        ),
    ]
