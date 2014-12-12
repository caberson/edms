# -*- coding: utf-8 -*-
from django.db import models

from core.models import Base
from location.models import Location

class Area(Base):
	location = models.ForeignKey(Location)
	name = models.CharField(u'Area Name (區域)', max_length=30, default='')

	def __unicode__(self):
		return u'{} - {}'.format(self.location, self.name)
