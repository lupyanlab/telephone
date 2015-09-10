# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='selection',
            field=models.OneToOneField(related_name='selection', null=True, to='grunt.Message'),
            preserve_default=True,
        ),
    ]
