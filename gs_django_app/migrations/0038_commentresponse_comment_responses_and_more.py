# Generated by Django 4.0.4 on 2022-04-21 09:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('gs_django_app', '0037_alter_post_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('like', 'like'), ('dislike', 'dislike')], max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'post_comments',
                'ordering': ('response', 'user', 'created_at'),
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='responses',
            field=models.ManyToManyField(related_name='comments_responded', through='gs_django_app.CommentResponse', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='responses',
            field=models.ManyToManyField(related_name='posts_responded', through='gs_django_app.PostResponse', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentresponse',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gs_django_app.comment'),
        ),
        migrations.AddField(
            model_name='commentresponse',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
