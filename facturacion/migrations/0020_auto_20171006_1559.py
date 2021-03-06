# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-06 18:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0020_auto_20171006_1553'),
        ('facturacion', '0019_purchase_billable'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1, verbose_name='quantity')),
                ('concept', models.TextField(max_length=500, verbose_name='concept')),
                ('date_created', models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Student', verbose_name='miembro')),
            ],
            options={
                'verbose_name_plural': 'Regalos',
                'verbose_name': 'Regalo',
                'permissions': (('save_gift', 'NEW: Can save changes made to the model'),),
            },
        ),
        migrations.AddField(
            model_name='product',
            name='inventory_entry',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='informacion.InventoryEntry', verbose_name='entrada de inventario'),
        ),
        migrations.AddField(
            model_name='gift',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Product'),
        ),
    ]
