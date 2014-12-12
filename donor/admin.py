import locale

from django.contrib import admin
from core.filters import YearSeasonListFilter
from donor.models import *
import student.models

locale.setlocale( locale.LC_ALL, '' )

class DonationInline(admin.TabularInline):
    model = Donation
    readonly_fields = ('dt', 'amount', 'receipt_number', 'notes', 'yr', 'season', 'require_attention',)
    extra = 0

class AssignmentInline(admin.TabularInline):
    model = student.models.Assignment
    # 'student', 
    readonly_fields = ('yr', 'season', 'assignment_amount', 'require_attention',)

    # readonly_fields = ('student', 'donor', 'year', 'season', 'assignment_amount', 'require_attention',)
    extra = 0
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # print self.donor.donation_country_limit
        # print request._obj_.donation_country_limit
        country = request._obj_.donation_country_limit
        if db_field.name == "student" and country != "":
            print "student >>>>>>>>>>>>>>>>>>>>>>>>> ", country

            kwargs["queryset"] = student.models.Student.objects.filter(school__area__location__country=country).order_by('name')


        return super(AssignmentInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
    

class DonorAdmin(admin.ModelAdmin):
    inlines = [
        DonationInline,
        AssignmentInline,
    ]
    list_display = ('eep_id', 'chi_name', 'eng_name', 
        'donation_info',
    )
    list_display_links = ('eep_id', 'chi_name', 'eng_name')
    ordering = ['eep_id']
    search_fields = ['=eep_id', 'chi_name', 'eng_name']

    def donation_info(self, obj):
        return u'${} - ${} = ${}'.format(
            obj.total_donation,
            obj.total_assignment,
            obj.total_donation - obj.total_assignment
        )
    donation_info.short_description = 'total donation - total assignment = remaining'

    def get_form(self, request, obj=None, **kwargs):
        # Save obj reference for future processing in Inline
        request._obj_ = obj
        return super(DonorAdmin, self).get_form(request, obj, **kwargs)

class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'donor_eep_id', 'donor', 'dt', 'amount', 'receipt_number', 'notes', 'yr_season', 'require_attention'
    )
    list_display_links = ('donor',)
    list_filter = (
        'require_attention',
        YearSeasonListFilter,
    )
    ordering = ['donor__eep_id', '-yr', 'season']
    # ordering = ['eep_id', '-yr', 'season']
    search_fields = ['=donor__eep_id']

    def eep_id(self):
        return self.donor.eep_id


admin.site.register(Donor, DonorAdmin)
admin.site.register(Donation, DonationAdmin)
# models = [Donation]
# admin.site.register(models)
