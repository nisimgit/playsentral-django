# Generated by Django 4.0.3 on 2022-04-06 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gs_django_app', '0025_post_remove_comment_thread_remove_game_threads_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gs_django_app.post'),
        ),
    ]
