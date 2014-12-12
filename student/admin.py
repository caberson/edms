from django.contrib import admin

from core.filters import YearSeasonListFilter
from student.models import *

class AttendingSchoolInline(admin.TabularInline):
    model = AttendingSchool
    extra = 1

class StudentAdmin(admin.ModelAdmin):
    inlines = [
        AttendingSchoolInline,
    ] 
    list_display = list_display_links = (
        'name', 'school', 'sex', 'cls', 'grad_yr', 'notes'
    )
    # list_filter = ('school__location__name', 'area__name')
    list_filter = (
        'school__area__location__country',
        'school__area__location__name',
        'school__area__name','school__name',
    )
    # not sure what does this do list_select_related = ('school__area__name',)
    ordering = ['school']
    search_fields = ['name']


class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'school',
        'donor',
        'yr_season',
        'assignment_amount',
        'require_attention',
    )
    list_display_links = (
        'student',#, 'school', 'donor', 'yr', 'season',
    )
    list_filter = (
        'require_attention',
        YearSeasonListFilter,
        # 'yr', 'season',
        'student__school__area__location',
        'student__school__area__name',
        #'donor',
    )
    raw_id_fields = ('student',)
    # readonly_fields = ('yr_season',)
    # not sure what does this do list_select_related = ('school__area__name',)
    ordering = ['yr']
    search_fields = ['=donor__eep_id', 'donor__chi_name']

    def school(self, obj):
        return obj.student.school
    


# models = [Student, AttendingSchool, Assignment]
# admin.site.register(models)
admin.site.register(Student, StudentAdmin)
admin.site.register(Assignment, AssignmentAdmin)
