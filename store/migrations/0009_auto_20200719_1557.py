# Generated by Django 3.0.7 on 2020-07-19 10:27

import datetime
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_auto_20200719_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='Use map widget for point the house location', srid=4326)),
            ],
            options={
                'verbose_name_plural': 'Locations',
            },
        ),
        migrations.AlterField(
            model_name='reviews',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 19, 10, 27, 47, 955434, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='addresss',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.Location'),
        ),
    ]
