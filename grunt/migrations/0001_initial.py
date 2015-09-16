# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import grunt.handlers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('seed', models.FileField(upload_to=b'seeds/')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('generation', models.IntegerField(default=0, editable=False)),
                ('audio', models.FileField(upload_to=grunt.handlers.message_file_name)),
                ('chain', models.ForeignKey(blank=True, to='grunt.Chain', null=True)),
                ('parent', models.ForeignKey(blank=True, to='grunt.Message', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='chain',
            name='game',
            field=models.ForeignKey(to='grunt.Game'),
            preserve_default=True,
        ),
    ]
