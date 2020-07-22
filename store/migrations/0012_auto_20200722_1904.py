# Generated by Django 3.0.7 on 2020-07-22 13:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_auto_20200722_1901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='miniorder',
            name='return_window',
            field=models.DateTimeField(default=datetime.datetime(2020, 8, 1, 19, 4, 50, 424110)),
        ),
        migrations.AlterField(
            model_name='return',
            name='return_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 22, 19, 4, 50, 428078)),
        ),
        migrations.AlterField(
            model_name='return',
            name='review_description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='reviews',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 22, 19, 4, 50, 428078), editable=False),
        ),
    ]
