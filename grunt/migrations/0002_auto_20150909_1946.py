# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import grunt.handlers


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='audio',
            field=models.FileField(max_length=200, upload_to=grunt.handlers.message_path, blank=True),
            preserve_default=True,
        ),
    ]
