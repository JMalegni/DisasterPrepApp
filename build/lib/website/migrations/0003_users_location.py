# Generated by Django 5.0.6 on 2024-06-14 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_remove_users_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='location',
            field=models.CharField(default='Unknown', max_length=50),
        ),
    ]