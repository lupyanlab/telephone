# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0002_auto_20151022_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='end_at',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
