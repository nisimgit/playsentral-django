# Generated by Django 4.0.3 on 2022-04-06 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gs_django_app', '0023_alter_game_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='thread',
            old_name='title',
            new_name='text',
        ),
    ]
