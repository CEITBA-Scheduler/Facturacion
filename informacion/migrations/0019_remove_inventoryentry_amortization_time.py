# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-06 17:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0018_mediaobject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryentry',
            name='amortization_time',
        ),
    ]