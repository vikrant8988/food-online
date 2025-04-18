# Generated by Django 5.1.7 on 2025-04-12 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_country_alter_order_state'),
        ('vendor', '0008_alter_openinghour_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='vendors',
            field=models.ManyToManyField(blank=True, to='vendor.vendor'),
        ),
    ]
