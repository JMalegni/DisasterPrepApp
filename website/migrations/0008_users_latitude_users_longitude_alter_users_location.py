# Generated by Django 5.0.6 on 2024-06-24 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_users_baby_bool_users_child_bool_users_women_bool'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='users',
            name='longitude',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='users',
            name='location',
            field=models.CharField(default='Unknown', max_length=255),
        ),
    ]
