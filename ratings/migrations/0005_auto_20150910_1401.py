# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0004_auto_20150910_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(related_name='choices', to='ratings.Question'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.OneToOneField(related_name='answer', null=True, blank=True, to='grunt.Message'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(related_name='questions', to='ratings.Survey'),
            preserve_default=True,
        ),
    ]
