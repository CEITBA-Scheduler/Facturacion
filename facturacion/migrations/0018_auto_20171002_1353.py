# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-02 16:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0017_auto_20170907_1716'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='debt',
            options={'permissions': (('save_debt', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Debt', 'verbose_name_plural': 'Debts'},
        ),
        migrations.AlterModelOptions(
            name='enrollment',
            options={'permissions': (('save_enrollment', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Enrollment', 'verbose_name_plural': 'Enrollments'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'permissions': (('save_product', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='purchase',
            options={'permissions': (('save_purchase', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Purchase', 'verbose_name_plural': 'Purchases'},
        ),
        migrations.AlterModelOptions(
            name='purchaseitem',
            options={'permissions': (('save_purchaseitem', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Purchase Item', 'verbose_name_plural': 'Purchase Items'},
        ),
        migrations.AlterModelOptions(
            name='reimbursement',
            options={'get_latest_by': 'date_created', 'permissions': (('save_reimbursement', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Reimbursement', 'verbose_name_plural': 'Reimbursements'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'get_latest_by': 'date_created', 'permissions': (('save_report', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Report', 'verbose_name_plural': 'Reports'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['name'], 'permissions': (('save_service', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Service', 'verbose_name_plural': 'Services'},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'permissions': (('save_student', 'NEW: Can save changes made to the model'),), 'verbose_name': 'Member', 'verbose_name_plural': 'Members'},
        ),
    ]
