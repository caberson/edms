# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('area', models.ForeignKey(to='area.Area', null=True)),
            ],
            options={
                'verbose_name': 'School (\u5b78\u6821)',
                'verbose_name_plural': 'Schools (\u5b78\u6821)',
            },
            bases=(models.Model,),
        ),
    ]
