# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_auto_20150910_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='selection',
            field=models.OneToOneField(related_name='selection', null=True, blank=True, to='grunt.Message'),
            preserve_default=True,
        ),
    ]
