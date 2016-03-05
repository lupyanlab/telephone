# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0003_auto_20151022_1554'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='edited',
            new_name='rejected',
        ),
    ]
