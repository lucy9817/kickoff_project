# Generated by Django 5.1.1 on 2024-10-15 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kick_off', '0006_remove_mission_user_remove_mission_video_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mission',
            old_name='example_image',
            new_name='video_url',
        ),
    ]
