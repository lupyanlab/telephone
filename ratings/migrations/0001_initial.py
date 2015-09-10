# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0002_auto_20150909_1946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.OneToOneField(related_name='answer', null=True, blank=True, to='grunt.Message')),
                ('choices', models.ManyToManyField(to='grunt.Message')),
                ('given', models.OneToOneField(related_name='given', to='grunt.Message')),
                ('selection', models.OneToOneField(related_name='selection', null=True, blank=True, to='grunt.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(related_name='questions', to='ratings.Survey'),
            preserve_default=True,
        ),
    ]
