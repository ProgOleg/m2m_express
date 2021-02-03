# Generated by Django 2.2 on 2021-02-02 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0023_comment_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='techsupport',
            options={'verbose_name_plural': 'Телефон тех поддержки'},
        ),
        migrations.AddField(
            model_name='order',
            name='date_changed',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='is_closed',
            field=models.BooleanField(default=False, verbose_name='Закрыт клиентом'),
        ),
    ]