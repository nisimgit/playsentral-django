# Generated by Django 4.0.4 on 2022-04-17 07:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gs_django_app', '0033_postlike_alter_post_comments_remove_post_likes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('like', 'like'), ('dislike', 'dislike')], max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'post_responses',
                'ordering': ('response', 'user', 'created_at'),
            },
        ),
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
        migrations.AddField(
            model_name='post',
            name='responses',
            field=models.ManyToManyField(related_name='posts_liked', through='gs_django_app.PostResponse', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='PostLike',
        ),
        migrations.AddField(
            model_name='postresponse',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gs_django_app.post'),
        ),
        migrations.AddField(
            model_name='postresponse',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
