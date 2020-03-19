# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 20:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(db_index=True, max_length=15, unique=True, verbose_name='bill number')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='amount')),
                ('date_created', models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created')),
                ('date_emitted', models.DateField(db_index=True, verbose_name='date emitted')),
                ('date_paid', models.DateField(db_index=True, verbose_name='date paid')),
            ],
            options={
                'verbose_name_plural': 'Bills',
                'verbose_name': 'Bill',
            },
        ),
        migrations.CreateModel(
            name='BillCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name_plural': 'Bill Categories',
                'verbose_name': 'Bill Category',
            },
        ),
        migrations.AddField(
            model_name='bill',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='informacion.BillCategory', verbose_name='category'),
        ),
    ]