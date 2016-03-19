# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transcribe', '0002_auto_20160304_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcription',
            name='message',
            field=models.ForeignKey(related_name='transcribed_messages', to='transcribe.MessageToTranscribe'),
        ),
    ]
