# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 06:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('charityapp', '0004_auto_20170219_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='sector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='charityapp.Sector'),
        ),
    ]
