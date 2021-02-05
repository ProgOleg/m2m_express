# Generated by Django 2.2 on 2021-02-04 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0026_auto_20210203_2306'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('NOT_SELECTED', 'NOT_SELECTED'), ('INVOICE', 'INVOICE'), ('BANK_CARD', 'BANK_CARD')], default='NOT_SELECTED', max_length=63, verbose_name='Тип оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='sdek_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='ID отделения'),
        ),
    ]
