# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0005_auto_20150910_1401'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='choice',
            unique_together=set([('question', 'message')]),
        ),
    ]
