# Generated by Django 4.0.3 on 2022-04-01 07:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gs_django_app', '0018_alter_game_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ('game', 'rating')},
        ),
        migrations.AlterModelOptions(
            name='series',
            options={'ordering': ('name',)},
        ),
    ]
