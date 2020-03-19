# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-28 22:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facturacion', '0012_auto_20160828_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='LockerAssignation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locker_id', models.PositiveSmallIntegerField(verbose_name='locker id')),
                ('date_created', models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created')),
                ('enrollment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Enrollment', verbose_name='enrollment')),
            ],
            options={
                'verbose_name': 'Locker Assignation',
                'verbose_name_plural': 'Locker Assignation',
            },
        ),
        migrations.CreateModel(
            name='LockerSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created')),
                ('count', models.PositiveSmallIntegerField(verbose_name='count')),
                ('service', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Service')),
            ],
            options={
                'verbose_name': 'Locker Site',
                'verbose_name_plural': 'Locker Sites',
            },
        ),
    ]
