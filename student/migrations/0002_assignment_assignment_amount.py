# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='assignment_amount',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
