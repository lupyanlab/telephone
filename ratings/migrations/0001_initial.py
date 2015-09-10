# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0002_auto_20150909_1946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.OneToOneField(related_name='messages', to='grunt.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.OneToOneField(related_name='answer', to='grunt.Message')),
                ('given', models.OneToOneField(related_name='given', to='grunt.Message')),
                ('selection', models.OneToOneField(related_name='selection', to='grunt.Message')),
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
            field=models.ForeignKey(to='ratings.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choices',
            name='question',
            field=models.ForeignKey(to='ratings.Question'),
            preserve_default=True,
        ),
    ]
