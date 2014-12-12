# -*- coding: utf-8 -*-

from django.db import models
# from django.core.signals import post_init
# from django.dispatch import receiver

from datetime import date

from core.models import Base, Season
import core.util
# from donor.models import Donor
from school.models import School

class Student(Base):
	MALE = 'm'
	FEMALE = 'f'
	SEX_CHOICES = (
		#('', 'NA'),
		(MALE, u'M (男)'),
		(FEMALE, u'F (女)'),
	)

	record_school_history = True

	name = models.CharField(u'Name (姓名)', max_length=50, unique=True)
	school = models.ForeignKey(School, default=None)
	sex = models.CharField(u'Sex (性別)', max_length=1, choices=SEX_CHOICES, default='')
	cls = models.CharField(u'Class (年級班別)', max_length=100, default='')
	# grad_yr = models.IntegerField(null=True)
	grad_yr = models.CharField(
		u'Graduation Year (畢業年份)', max_length=50, default='', null=True, blank=True
	)
	notes = models.TextField(null=True)

	@staticmethod
	def record_school_change(student, old_school, new_school, end_dt=None):
		if student.pk is None:
			return

		if old_school is None:
			return

		if old_school == new_school:
			return

		history = AttendingSchool()
		history.student = student
		history.school = old_school
		history.end_dt = (date.today() if end_dt is None else end_dt)
		history.save()

	def assign_to_donor(self, donor, yr, season, assignment_amount):
		require_attention = False
		if not isinstance(assignment_amount, int) or assignment_amount == 0:
			assignment_amount = None
			require_attention = True

		# Update assignment or create a new one
		try:
			# Update assignment
			assignment = Assignment.objects.get(
				student=self,
				donor=donor,
				yr=yr,
				season=season
				#assignment_amount=assignment_amount,
				#require_attention=require_attention
			)
		except:
			# New assignment.
			assignment = Assignment()
			assignment.student = self
			assignment.donor = donor
			assignment.yr = yr
			assignment.season = season

		assignment.assignment_amount = assignment_amount
		assignment.require_attention = require_attention

		assignment.save()
		return assignment

	"""
	@receiver(post_init)
	def post_init_callback(sender, instance, **kwargs):
		print sender
		print instance
		pass
	"""
	def save(self, *args, **kwargs):
		if self.record_school_history is True and self.pk is not None:
			prev = Student.objects.get(pk=self.pk)
			Student.record_school_change(self, prev.school, self.school)

		super(Student, self).save(*args, **kwargs)

	def __unicode__(self):
		return u'{}: {}'.format(self.school.area.location.country, self.name)


class AttendingSchool(Base):
	student = models.ForeignKey(Student)
	school = models.ForeignKey('school.School')
	end_dt = models.DateField(null=True, blank=True)

	def __unicode__(self):
		return self.student.name

class Assignment(Base):
	# TODO: Remove this
	SPRING = 's'
	FALL = 'f'
	SEASON_CHOICES = (
		(SPRING, u'Spring (春)'),
		(FALL, u'Fall (秋)'),
	)

	student = models.ForeignKey(Student)
	donor = models.ForeignKey('donor.Donor')
	yr = models.IntegerField(u'Year (年份)', default=core.util.get_current_year)
	season = models.CharField(
		u'Season (季節)', max_length=1, choices=Season.SEASON_CHOICES, default=Season.SPRING
	)
	assignment_amount = models.IntegerField(blank=True, null=True)
	require_attention = models.BooleanField(default=False)

	def yr_season(self):
		if self is None:
			return u''
		return u'{}-{}'.format(self.yr, Season.get_season_text(self.season))

	def __unicode__(self):
		return u'{}'.format(self.student.name)

		print u'{} {} {}{} {}'.format(
			self.student.name,
			self.donor.chi_name,
			self.yr,
			self.season,
			self.assignment_amount,
		)

