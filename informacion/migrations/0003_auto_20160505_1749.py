# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 20:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0002_auto_20160505_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='date_paid',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='date paid'),
        ),
    ]
