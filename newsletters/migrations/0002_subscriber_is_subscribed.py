# Generated by Django 3.2.23 on 2024-02-10 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='is_subscribed',
            field=models.BooleanField(default=True),
        ),
    ]