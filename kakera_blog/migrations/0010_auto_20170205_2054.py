# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakera_blog', '0009_auto_20170205_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticpage',
            name='cooked',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='excerpt',
            field=models.TextField(blank=True),
        ),
    ]