from django.shortcuts import render
# from django.http import HttpResponse
from django.views import generic

from student.models import *

# Create your views here.
class IndexView(generic.ListView):
	"""
	student_list = Student.objects.order_by('name')[:5]
	context = {'student_list': student_list}

	return render(request, 'student/index.html', context)
	"""
	template_name = 'student/index.html'
	context_object_name = 'student_list'

	def get_queryset(self):
		return Student.objects.order_by('name')
