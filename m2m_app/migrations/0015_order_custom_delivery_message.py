# Generated by Django 2.2 on 2021-01-28 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m2m_app', '0014_auto_20210128_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='custom_delivery_message',
            field=models.CharField(default=None, max_length=2056, null=True, verbose_name='Условия доставки'),
        ),
    ]
