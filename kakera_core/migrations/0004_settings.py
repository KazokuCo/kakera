# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-04 01:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('kakera_core', '0003_theme'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_username', models.CharField(blank=True, max_length=25)),
                ('facebook_username', models.CharField(blank=True, max_length=25)),
                ('patreon_username', models.CharField(blank=True, max_length=25)),
                ('discord_link', models.URLField(blank=True, max_length=255)),
                ('discourse_url', models.URLField(blank=True, max_length=255)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='settings', to='wagtailcore.Site')),
            ],
        ),
    ]
