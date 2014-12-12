# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.util


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dt', models.DateField()),
                ('amount', models.IntegerField()),
                ('receipt_number', models.IntegerField()),
                ('notes', models.TextField()),
                ('yr', models.IntegerField(default=core.util.get_current_year, verbose_name='Year (\u5e74\u4efd)')),
                ('season', models.CharField(default=b's', max_length=1, verbose_name='Season (\u5b63\u7bc0)', choices=[(b's', 'Spring (\u6625)'), (b'f', 'Fall (\u79cb)')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Donor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eep_id', models.IntegerField(null=True)),
                ('chi_name', models.CharField(unique=True, max_length=200)),
                ('eng_name', models.CharField(default=b'', max_length=200)),
                ('address', models.CharField(default=b'', max_length=200)),
                ('home_phone', models.CharField(default=b'', max_length=20, blank=True)),
                ('cell_phone', models.CharField(default=b'', max_length=20, blank=True)),
                ('office_phone', models.CharField(default=b'', max_length=20, blank=True)),
                ('email', models.CharField(default=b'', max_length=100)),
                ('donation_country_limit', models.CharField(default=b'', max_length=1, null=True, choices=[(b'c', b'China'), (b't', b'Taiwan')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(to='donor.Donor', null=True),
            preserve_default=True,
        ),
    ]
