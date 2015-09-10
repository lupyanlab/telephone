# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0002_auto_20150909_1946'),
        ('ratings', '0003_auto_20150910_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.OneToOneField(related_name='messages', to='grunt.Message')),
                ('question', models.ForeignKey(to='ratings.Question')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='choices',
            name='message',
        ),
        migrations.RemoveField(
            model_name='choices',
            name='question',
        ),
        migrations.DeleteModel(
            name='Choices',
        ),
    ]
