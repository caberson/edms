from django.contrib import admin
from school.models import *

class SchoolAdmin(admin.ModelAdmin):
	list_display = ('name', 'area')
	list_display_links = ('area', 'name')
	list_filter = ('area__location__name', 'area__name')

admin.site.register(School, SchoolAdmin)
# models = [School]
# admin.site.register(models)
