# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_enrollment_billable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reimbursement',
            name='concept',
            field=models.TextField(blank=True, max_length=500, verbose_name='concept'),
        ),
    ]