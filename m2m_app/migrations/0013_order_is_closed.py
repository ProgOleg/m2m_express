# Generated by Django 2.2 on 2021-01-24 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0012_auto_20210123_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]