# Generated by Django 3.0.7 on 2020-07-31 09:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0016_customerlocation_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_street_address', models.CharField(max_length=100, null=True)),
                ('billing_street_address_line_2', models.CharField(max_length=100, null=True)),
                ('billing_city', models.CharField(max_length=100, null=True)),
                ('billing_phone_number', models.BigIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('billing_postal_code', models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('shipping_street_address', models.CharField(max_length=100, null=True)),
                ('shipping_street_address_line_2', models.CharField(max_length=100, null=True)),
                ('shipping_city', models.CharField(max_length=100, null=True)),
                ('shipping_phone_number', models.BigIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('shipping_postal_code', models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('shipping_is_billing', models.BooleanField(default=True)),
                ('default', models.BooleanField(default=True)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.CustomerLocation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]