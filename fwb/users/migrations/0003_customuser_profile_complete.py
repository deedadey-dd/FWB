# Generated by Django 5.1.7 on 2025-04-17 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_complete',
            field=models.BooleanField(default=False),
        ),
    ]
