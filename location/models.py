# -*- coding: utf-8 -*-

from django.db import models

from core.models import Base

class Location(Base):
	TAIWAN = 't'
	CHINA = 'c'
	COUNTRY_CHOICES = (
		(CHINA, 'China'),
		(TAIWAN, 'Taiwan'),
	)

	country = models.CharField(max_length=1, choices=COUNTRY_CHOICES, default=CHINA)
	name = models.CharField(u'Location Name (地點)', max_length=30, default='')
	# area = models.CharField(u'Area (區域)', max_length=30)

	def __unicode__(self):
		return u'{}'.format(self.name)
