# Generated by Django 3.0.6 on 2020-05-27 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bubbleworld', '0008_auto_20200527_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='privilege',
            field=models.IntegerField(default=0, verbose_name='权限'),
        ),
    ]
