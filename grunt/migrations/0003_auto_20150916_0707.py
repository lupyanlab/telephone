# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0002_auto_20150916_0518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chain',
            name='seed',
        ),
        migrations.RemoveField(
            model_name='message',
            name='alive',
        ),
        migrations.AddField(
            model_name='message',
            name='num_children',
            field=models.IntegerField(default=1),
        ),
    ]
