# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 20:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0002_auto_20171013_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventinscription',
            name='extra_info',
            field=models.CharField(blank=True, default=None, max_length=400, null=True, verbose_name='informacion extra'),
        ),
    ]