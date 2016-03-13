# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0003_auto_20150918_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='name',
            field=models.CharField(unique=True, max_length=30),
        ),
    ]
