# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transcribe', '0003_auto_20160319_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcriptionsurvey',
            name='catch_trial_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
