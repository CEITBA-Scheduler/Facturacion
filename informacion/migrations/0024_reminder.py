# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-08 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0023_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='contenido')),
                ('completed', models.BooleanField(help_text='Marquelo para marcar el recordatorio como completado', verbose_name='completado')),
            ],
            options={
                'verbose_name': 'Recordatorio',
                'verbose_name_plural': 'Recordatorios',
                'permissions': (('save_mediaobject', 'NEW: Can save changes made to the model'),),
            },
        ),
    ]
