# Generated by Django 2.2 on 2021-01-11 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0003_customusers_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customusers',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]