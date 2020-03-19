# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-08 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0025_rangedexport'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rangedexport',
            options={'permissions': (('save_mediaobject', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Exportar por Rango', 'verbose_name_plural': 'Exportar por Rango'},
        ),
        migrations.AlterField(
            model_name='rangedexport',
            name='end_date',
            field=models.DateField(verbose_name='fecha fin'),
        ),
    ]
