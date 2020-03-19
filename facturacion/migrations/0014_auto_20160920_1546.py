# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-20 18:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0013_service_single_subscription'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['name'], 'permissions': (('save_model', 'Can save changes made to the model'),), 'verbose_name': 'Service', 'verbose_name_plural': 'Services'},
        ),
        migrations.AlterField(
            model_name='service',
            name='single_subscription',
            field=models.BooleanField(db_index=True, default=True, help_text='Unmark this box to allow more than one subscription per member', verbose_name='single subscription'),
        ),
        migrations.AlterField(
            model_name='service',
            name='type',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Locker'), ('C', 'Language Course')], default='N', max_length=1, verbose_name='type'),
        ),
    ]