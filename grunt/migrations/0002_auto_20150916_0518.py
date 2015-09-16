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
            name='alive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='chain',
            name='game',
            field=models.ForeignKey(related_name='chains', to='grunt.Game'),
        ),
        migrations.AlterField(
            model_name='message',
            name='chain',
            field=models.ForeignKey(related_name='messages', blank=True, to='grunt.Chain', null=True),
        ),
    ]
