# Generated by Django 4.0.4 on 2022-04-16 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gs_django_app', '0031_alter_rating_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
