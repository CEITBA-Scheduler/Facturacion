# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-02 16:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lockers', '0008_auto_20160922_1812'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lockerassignation',
            options={'ordering': ['locker_id'], 'permissions': (('save_lockerassignation', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Locker Assignation', 'verbose_name_plural': 'Locker Assignation'},
        ),
        migrations.AlterModelOptions(
            name='lockerhold',
            options={'ordering': ['date_created'], 'permissions': (('save_lockerhold', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Locker Hold', 'verbose_name_plural': 'Locker Hold'},
        ),
        migrations.AlterModelOptions(
            name='lockerqueue',
            options={'ordering': ['locker_site', 'date_created'], 'permissions': (('save_lockerqueue', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Locker Queue', 'verbose_name_plural': 'Locker Queue'},
        ),
        migrations.AlterModelOptions(
            name='lockersite',
            options={'permissions': (('save_lockersite', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Locker Site', 'verbose_name_plural': 'Locker Sites'},
        ),
    ]
