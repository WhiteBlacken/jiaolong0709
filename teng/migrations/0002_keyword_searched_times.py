# Generated by Django 3.2.5 on 2021-07-26 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teng', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='searched_times',
            field=models.IntegerField(default=0),
        ),
    ]
