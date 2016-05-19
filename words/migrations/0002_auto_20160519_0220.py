# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='word',
            name='survey',
        ),
        migrations.AlterField(
            model_name='question',
            name='word',
            field=models.CharField(max_length=60),
        ),
        migrations.DeleteModel(
            name='Word',
        ),
    ]
