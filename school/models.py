# -*- coding: utf-8 -*-
from django.db import models

from core.models import Base
from area.models import Area
		
class School(Base):
	class Meta:
		verbose_name = u'School (學校)'
		verbose_name_plural = u'Schools (學校)'


	name = models.CharField(max_length=30)
	area = models.ForeignKey(Area, null=True)

	def __unicode__(self):
		return u'({}) {}'.format(self.area, self.name)