# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Sum

from core.models import Base, Season
import core.util
from location.models import Location
from student.models import Assignment


class Donor(Base):
	eep_id = models.IntegerField(null=True)
	chi_name = models.CharField(max_length=200, unique=True)
	eng_name = models.CharField(max_length=200, default='')
	address = models.CharField(max_length=200, default='')
	home_phone = models.CharField(max_length=20, blank=True, default='')
	cell_phone = models.CharField(max_length=20, blank=True, default='')
	office_phone = models.CharField(max_length=20, blank=True, default='')
	email = models.CharField(max_length=100, default='')# models.EmailField(default='')
	donation_country_limit = models.CharField(
		max_length=1, blank=True, null=True, choices=Location.COUNTRY_CHOICES, default=''
	)

	def save(self, *args, **kwargs):
		if self.eep_id >= 3000:
			self.donation_country_limit = Location.CHINA

		super(Donor, self).save(*args, **kwargs)

	@property
	def total_donation(self):
		qs = Donation.objects.filter(donor__eep_id=self.eep_id)
		qs = qs.aggregate(total=Sum('amount'))
		total = 0 if qs['total'] is None else qs['total']
		
		return total
	
	@property
	def total_assignment(self):
		qs = Assignment.objects.filter(donor__eep_id=self.eep_id)
		qs = qs.aggregate(total=Sum('assignment_amount'))
		total = 0 if qs['total'] is None else qs['total']

		return total

	"""
	def __str__(self):
		return self.__unicode__()
	DUPLICATES
	馬秀琴阿姨 (row 654)
	James Dernehl 叔叔 (row 823)
	"""

	def __unicode__(self):
		return u"{}. {}".format(
			self.eep_id,
			(self.chi_name if self.chi_name else self.eng_name)
		)

class Donation(Base):
	donor = models.ForeignKey(Donor, null=True)
	dt = models.DateField(null=True)
	amount = models.IntegerField()
	receipt_number = models.CharField(max_length=50, blank=True, null=True, default="")
	notes = models.TextField(null=True)
	yr = models.IntegerField(u'Year (年份)', default=core.util.get_current_year)
	season = models.CharField(
		u'Season (季節)', max_length=1, choices=Season.SEASON_CHOICES, default=Season.SPRING
	)
	require_attention = models.BooleanField(default=False)

	@property
	def donor_eep_id(self):
		return u'{}'.format(self.donor.eep_id)

	def yr_season(self):
		return u'{}-{}'.format(self.yr, Season.get_season_text(self.season))

	def __unicode__(self):
		return u"({}) {} dt: {} {}{} ${} Notes: {}".format(
			self.donor.eep_id,
			self.donor.chi_name,
			self.dt,
			self.yr,
			self.season,
			self.amount,
			self.notes
		)
	