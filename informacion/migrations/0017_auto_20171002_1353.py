# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-02 16:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0016_auto_20170908_1506'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alquilermate',
            options={'permissions': (('save_alquilermate', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Alquiler de Mate', 'verbose_name_plural': 'Alquileres de Mate'},
        ),
        migrations.AlterModelOptions(
            name='inventorycategory',
            options={'permissions': (('save_inventorycategory', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Categoría de inventario', 'verbose_name_plural': 'Categoras de inventario'},
        ),
        migrations.AlterModelOptions(
            name='inventoryentry',
            options={'permissions': (('save_inventoryentry', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Entrada de inventario', 'verbose_name_plural': 'Entradas de inventario'},
        ),
        migrations.AlterModelOptions(
            name='journalentry',
            options={'permissions': (('save_journalentry', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Entrada de Libro Diario', 'verbose_name_plural': 'Entradas de Libro Diario'},
        ),
        migrations.AlterModelOptions(
            name='printercount',
            options={'permissions': (('save_printercount', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Cuenta de Impresión', 'verbose_name_plural': 'Cuentas de Impresión'},
        ),
        migrations.AlterModelOptions(
            name='printerreport',
            options={'get_latest_by': 'date_uploaded', 'permissions': (('save_printerreport', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Reporte de impresión', 'verbose_name_plural': 'Reportes de impresión'},
        ),
        migrations.AlterModelOptions(
            name='printingexception',
            options={'permissions': (('save_printingexception', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Excepcion de Impresion', 'verbose_name_plural': 'Excepciones de Impresiones'},
        ),
        migrations.AlterModelOptions(
            name='sportcertificate',
            options={'get_latest_by': 'date_emitted', 'permissions': (('save_sportcertificate', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Certificado médico', 'verbose_name_plural': 'Certificados médicos'},
        ),
        migrations.AlterModelOptions(
            name='ymcafamilymember',
            options={'permissions': (('save_ymcafamilymember', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Miembro familiar del YMCA', 'verbose_name_plural': 'Miembros familiares del YMCA'},
        ),
    ]
