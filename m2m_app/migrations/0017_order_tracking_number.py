# Generated by Django 2.2 on 2021-01-30 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0016_auto_20210129_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='Трекинг номер'),
        ),
    ]
