# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_assignment_assignment_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='require_attention',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
