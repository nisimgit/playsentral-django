# Generated by Django 4.0.4 on 2022-04-21 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gs_django_app', '0038_commentresponse_comment_responses_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='description',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterModelTable(
            name='commentresponse',
            table='comment_responses',
        ),
    ]
