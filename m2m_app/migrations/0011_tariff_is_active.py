# Generated by Django 2.2 on 2021-01-23 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0010_auto_20210123_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='tariff',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]