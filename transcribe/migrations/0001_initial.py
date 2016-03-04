# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0003_auto_20151022_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageToTranscribe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('given', models.ForeignKey(related_name='transcribe_questions', to='grunt.Message')),
            ],
        ),
        migrations.CreateModel(
            name='Transcription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=60)),
                ('message', models.ForeignKey(related_name='transcriptions', to='transcribe.MessageToTranscribe')),
            ],
        ),
        migrations.CreateModel(
            name='TranscriptionSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('num_transcriptions_per_taker', models.IntegerField(default=10)),
            ],
        ),
        migrations.AddField(
            model_name='messagetotranscribe',
            name='survey',
            field=models.ForeignKey(related_name='messages', to='transcribe.TranscriptionSurvey'),
        ),
    ]
