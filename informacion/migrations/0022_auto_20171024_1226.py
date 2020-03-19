# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-24 15:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0026_auto_20171023_1459'),
        ('informacion', '0021_inventoryentry_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lended_object', models.TextField(verbose_name='objeto prestado')),
                ('time_taken', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Fecha de prestamo')),
                ('time_returned', models.DateTimeField(blank=True, default=None, null=True, verbose_name='fecha de devolución')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Student', verbose_name='miembro')),
            ],
            options={
                'verbose_name': 'Prestamo',
                'verbose_name_plural': 'Prestamos',
                'permissions': (('save_lend', 'NEW: Can save changes made to the model'),),
            },
        ),
        migrations.AlterField(
            model_name='mediaobject',
            name='screen_time',
            field=models.PositiveSmallIntegerField(help_text='En segundos', verbose_name='tiempo en pantalla'),
        ),
    ]