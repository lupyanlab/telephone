# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0002_auto_20150909_1946'),
        ('ratings', '0006_auto_20150910_1557'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='choice',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='choice',
            name='message',
        ),
        migrations.RemoveField(
            model_name='choice',
            name='question',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.AddField(
            model_name='question',
            name='choices',
            field=models.ManyToManyField(to='grunt.Message'),
            preserve_default=True,
        ),
    ]
