# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0002_auto_20160519_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='catch_trial_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
