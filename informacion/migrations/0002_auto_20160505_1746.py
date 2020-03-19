# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='description',
            field=models.TextField(blank=True, max_length=500, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='bill',
            name='date_paid',
            field=models.DateField(blank=True, db_index=True, verbose_name='date paid'),
        ),
    ]
