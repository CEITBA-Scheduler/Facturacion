# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-19 22:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0015_auto_20161004_1606'),
        ('informacion', '0009_inventorycategory_inventoryentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='YMCAFamilyMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family_members', models.TextField(help_text='Un familiar por linea.', verbose_name='Familiares')),
                ('enrollment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Enrollment', verbose_name='enrollment')),
            ],
            options={
                'verbose_name_plural': 'Miembros familiares del YMCA',
                'verbose_name': 'Miembro familiar del YMCA',
                'permissions': (('save_model', 'Can save changes made to the model'),),
            },
        ),
        migrations.AlterField(
            model_name='inventoryentry',
            name='location',
            field=models.CharField(max_length=100, verbose_name='ubicación'),
        ),
    ]
