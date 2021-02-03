# Generated by Django 2.2 on 2021-02-03 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0025_auto_20210202_2234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-date_created'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='order',
            name='is_finished',
            field=models.BooleanField(default=False, verbose_name='Завершен'),
        ),
    ]