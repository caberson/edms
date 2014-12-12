# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.util


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0001_initial'),
        ('donor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yr', models.IntegerField(default=core.util.get_current_year, verbose_name='Year (\u5e74\u4efd)')),
                ('season', models.CharField(default=b's', max_length=1, verbose_name='Season (\u5b63\u7bc0)', choices=[(b's', 'Spring (\u6625)'), (b'f', 'Fall (\u79cb)')])),
                ('donor', models.ForeignKey(to='donor.Donor')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttendingSchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('end_dt', models.DateField(null=True, blank=True)),
                ('school', models.ForeignKey(to='school.School')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Name (\u59d3\u540d)')),
                ('sex', models.CharField(default=b'', max_length=1, verbose_name='Sex (\u6027\u5225)', choices=[(b'm', 'M (\u7537)'), (b'f', 'F (\u5973)')])),
                ('cls', models.CharField(default=b'', max_length=100, verbose_name='Class (\u5e74\u7d1a\u73ed\u5225)')),
                ('grad_yr', models.CharField(default=b'', max_length=50, null=True, verbose_name='Graduation Year (\u7562\u696d\u5e74\u4efd)', blank=True)),
                ('notes', models.TextField(null=True)),
                ('school', models.ForeignKey(default=None, to='school.School')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attendingschool',
            name='student',
            field=models.ForeignKey(to='student.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='student',
            field=models.ForeignKey(to='student.Student'),
            preserve_default=True,
        ),
    ]
