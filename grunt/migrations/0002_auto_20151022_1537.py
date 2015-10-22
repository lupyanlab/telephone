# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='end_at',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='start_at',
            field=models.FloatField(default=0.0),
        ),
    ]
