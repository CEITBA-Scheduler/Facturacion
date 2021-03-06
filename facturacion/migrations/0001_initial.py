# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-16 02:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import facturacion.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='date created')),
            ],
            options={
                'verbose_name_plural': 'Enrollments',
                'verbose_name': 'Enrollment',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('price', models.PositiveSmallIntegerField(verbose_name='price')),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='date created')),
                ('active', models.BooleanField(default=True, help_text="Once disabled, it can't be enabled again.", verbose_name='active')),
            ],
            options={
                'verbose_name_plural': 'Products',
                'verbose_name': 'Product',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='date')),
            ],
            options={
                'verbose_name_plural': 'Purchases',
                'verbose_name': 'Purchase',
            },
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Product')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Purchase')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='name')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='price')),
                ('date_created', models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created')),
                ('date_removed', models.DateField(blank=True, db_index=True, null=True, verbose_name='date removed')),
            ],
            options={
                'verbose_name_plural': 'Services',
                'verbose_name': 'Service',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='name')),
                ('student_id', models.PositiveIntegerField(unique=True, verbose_name='id')),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='date created')),
                ('date_removed', models.DateField(null=True, verbose_name='date removed')),
                ('active', models.BooleanField(default=True, help_text='Is it an active member of CEITBA?', verbose_name='active')),
            ],
            options={
                'verbose_name_plural': 'Students',
                'verbose_name': 'Student',
                'default_permissions': ('add', 'change'),
            },
        ),
        migrations.AddField(
            model_name='purchase',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Student', verbose_name='student'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Service', verbose_name='service'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Student', verbose_name='student'),
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'verbose_name': 'Student', 'verbose_name_plural': 'Students'},
        ),
        migrations.AddField(
            model_name='enrollment',
            name='date_removed',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='date removed'),
        ),
        migrations.AddField(
            model_name='product',
            name='date_removed',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='date removed'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='price'),
        ),
        migrations.RemoveField(
            model_name='product',
            name='active',
        ),
        migrations.RemoveField(
            model_name='student',
            name='active',
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='date created')),
                ('filename', models.CharField(default='', max_length=200, verbose_name='file name')),
                ('totalin', models.PositiveIntegerField(default=0, verbose_name='total earnings')),
                ('totalout', models.PositiveIntegerField(default=0, verbose_name='total losses')),
            ],
            options={
                'verbose_name_plural': 'Reports',
                'verbose_name': 'Report',
            },
        ),
        migrations.RenameField(
            model_name='purchase',
            old_name='date',
            new_name='date_created',
        ),
        migrations.AddField(
            model_name='enrollment',
            name='reported_in',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='facturacion.Report'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='reported_in',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='facturacion.Report'),
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'get_latest_by': 'date_created', 'verbose_name': 'Report', 'verbose_name_plural': 'Reports'},
        ),
        migrations.RemoveField(
            model_name='report',
            name='filename',
        ),
        migrations.AddField(
            model_name='report',
            name='report_file',
            field=models.FileField(default=None, upload_to='reports/', verbose_name='report file'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.PositiveIntegerField(db_index=True, unique=True, verbose_name='id'),
        ),
        migrations.AddField(
            model_name='report',
            name='active_members',
            field=models.PositiveIntegerField(default=0, verbose_name='active members'),
        ),
        migrations.AddField(
            model_name='report',
            name='students',
            field=models.PositiveIntegerField(default=0, verbose_name='students count'),
        ),
        migrations.AddField(
            model_name='report',
            name='subscriptions',
            field=models.PositiveIntegerField(default=0, verbose_name='subscriptions'),
        ),
        migrations.AddField(
            model_name='report',
            name='unsubscriptions',
            field=models.PositiveIntegerField(default=0, verbose_name='unsubscriptions'),
        ),
        migrations.AlterField(
            model_name='report',
            name='totalin',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='total earnings'),
        ),
        migrations.AlterField(
            model_name='report',
            name='totalout',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='total losses'),
        ),
        migrations.CreateModel(
            name='Reimbursement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(default=datetime.date.today, verbose_name='date created')),
                ('concept', models.TextField(max_length=500, verbose_name='concept')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='amount')),
            ],
        ),
        migrations.AlterField(
            model_name='report',
            name='date_created',
            field=models.DateField(default=datetime.date.today, verbose_name='to date'),
        ),
        migrations.AddField(
            model_name='reimbursement',
            name='reported_in',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='facturacion.Report'),
        ),
        migrations.AddField(
            model_name='reimbursement',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Student', verbose_name='student'),
        ),
        migrations.AlterModelOptions(
            name='reimbursement',
            options={'get_latest_by': 'date_created', 'verbose_name': 'Reimbursement', 'verbose_name_plural': 'Reimbursements'},
        ),
        migrations.AlterModelOptions(
            name='purchaseitem',
            options={'verbose_name': 'Purchase Item', 'verbose_name_plural': 'Purchase Items'},
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.Product', verbose_name='product'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='quantity'),
        ),
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(db_index=True, max_length=300, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='date_created',
            field=models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='product',
            name='date_created',
            field=models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='date_created',
            field=models.DateField(db_index=True, default=datetime.date.today, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='reimbursement',
            name='date_created',
            field=models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='student',
            name='date_created',
            field=models.DateField(db_index=True, default=datetime.date.today, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='student',
            name='date_removed',
            field=models.DateField(db_index=True, null=True, verbose_name='date removed'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='reported_in2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_in2', to='facturacion.Report'),
        ),
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, help_text='It must be an @itba.edu.ar email address.', max_length=254, validators=[facturacion.models.validate_itba_email], verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='student',
            name='date_removed',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='date removed'),
        ),
    ]
