# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 16:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kakera_core', '0014_auto_20170204_1143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customrendition',
            name='filter',
        ),
    ]
