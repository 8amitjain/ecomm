# Generated by Django 3.0.7 on 2020-07-31 08:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_customeraddress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeraddress',
            name='billing_phone_number',
            field=models.BigIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999999999)]),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='shipping_phone_number',
            field=models.BigIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999999999)]),
        ),
    ]