# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0005_message_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choices', models.ManyToManyField(related_name='word_questions', to='grunt.Message')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.ForeignKey(related_name='responses', to='words.Question')),
                ('selection', models.ForeignKey(related_name='word_responses', to='grunt.Message')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('num_questions_per_player', models.IntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=60)),
                ('survey', models.ForeignKey(to='words.Survey')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(related_name='questions', to='words.Survey'),
        ),
        migrations.AddField(
            model_name='question',
            name='word',
            field=models.ForeignKey(related_name='questions', to='words.Word'),
        ),
    ]
