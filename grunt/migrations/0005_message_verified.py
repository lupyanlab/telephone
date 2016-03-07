# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0004_auto_20160305_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
