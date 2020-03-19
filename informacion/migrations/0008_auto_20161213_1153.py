# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-13 14:53
from __future__ import unicode_literals

from django.db import migrations, models
import informacion.models


class Migration(migrations.Migration):

    dependencies = [
        ('informacion', '0007_auto_20161212_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportcertificate',
            name='certificate',
            field=models.FileField(upload_to=informacion.models.build_certificate_filename, verbose_name='certificate'),
        ),
    ]