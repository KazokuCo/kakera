# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-07 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakera_core', '0018_theme_extra_head'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='extra_body_end',
            field=models.TextField(blank=True),
        ),
    ]