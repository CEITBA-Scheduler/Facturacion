# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0016_auto_20170907_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='report_accounting_file',
            field=models.FileField(null=True, upload_to='reports/', verbose_name='Reporte de tesorería'),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_staff_file',
            field=models.FileField(null=True, upload_to='reports/', verbose_name='staff report file'),
        ),
    ]