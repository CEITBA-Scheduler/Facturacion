# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-22 18:06
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0008_auto_20161213_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Categoría de inventario',
                'verbose_name_plural': 'Categoras de inventario',
                'permissions': (('save_model', 'Can save changes made to the model'),),
            },
        ),
        migrations.CreateModel(
            name='InventoryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='fecha de entrada')),
                ('description', models.TextField(max_length=500, verbose_name='description')),
                ('location', models.CharField(max_length=100, verbose_name='location')),
                ('original_value', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='valor de adquisición')),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='cantidad')),
                ('amortization_time', models.PositiveSmallIntegerField(verbose_name='tiempo de amortización')),
                ('acquired', models.BooleanField(default=True, verbose_name='adquirido')),
                ('categories', models.ManyToManyField(to='informacion.InventoryCategory', verbose_name='categorias')),
                ('journal_entries', models.ManyToManyField(to='informacion.JournalEntry', verbose_name='entradas del libro diario')),
            ],
            options={
                'verbose_name': 'Entrada de inventario',
                'verbose_name_plural': 'Entradas de inventario',
                'permissions': (('save_model', 'Can save changes made to the model'),),
            },
        ),
    ]
