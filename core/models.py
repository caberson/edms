# -*- coding: utf-8 -*-

# from datetime import date

from django.db import models

class Base(models.Model):
	class Meta:
		abstract = True

class Season():
	SPRING = 's'
	FALL = 'f'
	SEASON_CHOICES = (
		(SPRING, u'Spring (春)'),
		(FALL, u'Fall (秋)'),
	)

	@staticmethod
	def get_season_text(season):
		SEASON_TEXT = {
			Season.SPRING: u'Spring (春)',
			Season.FALL: u'Fall (秋)',
		}
		return SEASON_TEXT[season]