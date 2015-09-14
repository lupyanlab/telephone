# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_auto_20150914_0401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='selection',
            field=models.ForeignKey(to='grunt.Message'),
            preserve_default=True,
        ),
    ]
