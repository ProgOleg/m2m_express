# Generated by Django 2.2 on 2021-01-23 12:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0009_auto_20210123_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersprofilephysicalentrepreneur',
            name='scan_copy_img',
            field=models.ImageField(blank=True, null=True, upload_to='scan_copy/img/', verbose_name='Скан фото'),
        ),
        migrations.AlterField(
            model_name='usersprofilephysicalentrepreneur',
            name='scan_copy_pdf',
            field=models.FileField(blank=True, null=True, upload_to='scan_copy/pdf/', validators=[django.core.validators.FileExtensionValidator(['pdf'])], verbose_name='Скфан pdf'),
        ),
    ]
