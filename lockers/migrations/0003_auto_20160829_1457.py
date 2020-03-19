# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-29 17:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lockers', '0002_auto_20160829_1355'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lockerassignation',
            options={'ordering': ['locker_id'], 'permissions': (('save_model', 'Can save changes made to the model'),), 'verbose_name': 'Locker Assignation', 'verbose_name_plural': 'Locker Assignation'},
        ),
        migrations.AlterModelOptions(
            name='lockerqueue',
            options={'ordering': ['locker_site', 'date_created'], 'permissions': (('save_model', 'Can save changes made to the model'),), 'verbose_name': 'Locker Queue', 'verbose_name_plural': 'Locker Queue'},
        ),
        migrations.AlterModelOptions(
            name='lockersite',
            options={'permissions': (('save_model', 'Can save changes made to the model'),), 'verbose_name': 'Locker Site', 'verbose_name_plural': 'Locker Sites'},
        ),
    ]
