# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-27 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0023_auto_20171127_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediaobject',
            name='published_apuntes',
            field=models.BooleanField(db_index=True, default=True, verbose_name='publicado en apuntes'),
        ),
        migrations.AddField(
            model_name='mediaobject',
            name='published_web',
            field=models.BooleanField(db_index=True, default=True, verbose_name='publicado en web'),
        ),
        migrations.AlterField(
            model_name='mediaobject',
            name='published_tv',
            field=models.BooleanField(db_index=True, default=True, verbose_name='publicado en tv'),
        ),
    ]
