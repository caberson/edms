# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(default=b'c', max_length=1, choices=[(b'c', b'China'), (b't', b'Taiwan')])),
                ('name', models.CharField(default=b'', max_length=30, verbose_name='Location Name (\u5730\u9ede)')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
