# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0002_auto_20141208_0153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='receipt_number',
            field=models.CharField(default=b'', max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
