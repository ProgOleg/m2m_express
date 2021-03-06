# Generated by Django 2.2 on 2021-01-15 12:32

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0006_auto_20210113_1940'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(max_length=255, verbose_name='Название компании')),
                ('specification', models.CharField(max_length=255, verbose_name='Описание')),
                ('link', models.CharField(max_length=2000, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('locations', models.CharField(max_length=255, verbose_name='Локации')),
                ('sms', models.CharField(max_length=255, verbose_name='Стоимость SMS')),
                ('megabyte', models.CharField(max_length=255, verbose_name='Стоимость MB')),
                ('cost', models.CharField(max_length=255, verbose_name='Стоимость')),
            ],
            options={
                'verbose_name': 'Тариф',
                'verbose_name_plural': 'Тарифы',
            },
        ),
        migrations.RemoveField(
            model_name='usersprofilephysicalentrepreneur',
            name='scan_copy',
        ),
        migrations.AddField(
            model_name='usersprofilephysicalentrepreneur',
            name='scan_copy_img',
            field=models.ImageField(null=True, unique=True, upload_to='scan_copy/img/', verbose_name='Скан фото'),
        ),
        migrations.AddField(
            model_name='usersprofilephysicalentrepreneur',
            name='scan_copy_pdf',
            field=models.FileField(null=True, unique=True, upload_to='scan_copy/pdf/', validators=[django.core.validators.FileExtensionValidator(['pdf'])], verbose_name='Скфан pdf'),
        ),
        migrations.AlterField(
            model_name='customusers',
            name='mailing_status',
            field=models.BooleanField(default=False, verbose_name='Статус рассылки'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('address_sdek', models.CharField(max_length=1000, verbose_name='Адресс СДЭК')),
                ('tariff', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='m2m_app.Tariff', verbose_name='Тариф')),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказаы',
            },
        ),
    ]
