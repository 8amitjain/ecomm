# Generated by Django 3.0.7 on 2020-07-31 08:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200731_1408'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customeraddress',
            options={},
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]