# Generated by Django 2.2 on 2021-01-30 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0019_auto_20210130_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['date_created'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказаы'},
        ),
    ]
