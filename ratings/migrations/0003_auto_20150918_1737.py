# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_survey_num_questions_per_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.ForeignKey(related_name='answer', to='grunt.Message', null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='given',
            field=models.ForeignKey(related_name='given', to='grunt.Message'),
        ),
    ]
