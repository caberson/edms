# -*- coding: utf-8 -*-
import sys
import re
from datetime import datetime, date, timedelta

from django.core.management.base import BaseCommand, CommandError
from location.models import Location
from area.models import Area
from school.models import School
from donor.models import Donor
from student.models import Student, Assignment

import xlrd

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Import EEP data.'

    def handle(self, *args, **options):
        fn = u'/Users/cc/Desktop/2014年秋季助學名冊.xlsm'
        # wb = xlrd.open_workbook(fn, on_demand=True, formatting_info=True)
        wb = xlrd.open_workbook(fn, on_demand=True)

        # self.import_donors(wb)
        # self.import_sheets(wb)

        # Starts at sheet index 9.  Before that, format is different.
        # China student info
        # sn = 21
        # Taiwan student info
        sn = 22
        sn = 10
        sn = 9
        self.import_students(wb, sn)
        sn = 11
        self.import_students(wb, sn)
        sn = 12
        self.import_students(wb, sn)
        

        for a in args:
            """
            try:
                poll = Poll.objects.get(pk=int(poll_id))
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write('Successfully closed poll "%s"' % poll_id)
            """
            pass

    def import_sheets(self, wb):
        for i, name in enumerate(wb.sheet_names()):
            info = self.get_info_from_sheet_name(name)
            if info is None:
                continue

            print i, name, info
            # self.import_students(self, wb, i)

    def get_info_from_sheet_name(self, name):
        try:
            yr = 2000 + int(re.match(r'\d+', name).group())
            country = 'c' if name.find(u'中國') >= 0 else 't'
            season = Assignment.SPRING if name.find(u'春') >= 0 else Assignment.FALL
            return {
                'country': country,
                'season': season,
                'yr': yr
            }
        except:
            pass

        return None

    def import_students(self, wb, sheet_index):
        colpos = {                                                                  
            'region': 1,                                                            
            'location': 2,                                                          
            'school': 3,                                                            
            'donor_balance': 4,                                                     
            'student_name': 5,                                                      
            'sex': 6,                                                               
            'grade': 7,                                                             
            'graduation_year': 8,                                                   
            'student_donor_id': 9,                                                  
            'student_donor_name': 10,                                               
            'student_donor_donation_amount_local': 11,                              
            'student_donor_donation_amount_us': 12,                                 
            'comment': 13,                                                          
            'comment_tw': 14,                                                       
        }                 


        # Location.objects.all().delete()
        # Area.objects.all().delete()
        # Student.objects.all().delete()

        sheet = wb.sheet_by_index(sheet_index)
        sheet_info = self.get_info_from_sheet_name(sheet.name)
        if sheet_info['country'] == Location.TAIWAN:
            comment_pos = colpos['comment_tw']
        else:
            comment_pos = colpos['comment'] 

        if sheet_info['season'] == Assignment.SPRING:
            dt = '1/1/{}'
        else:
            dt = '6/1/{}'
        school_end_dt = datetime.strptime(dt.format(sheet_info['yr']), '%m/%d/%Y')
        school_end_dt -= timedelta(seconds=1)
        print school_end_dt
        print sheet.number, sheet.name, sheet_info

        start_row = 3
        end_row = 3070
        for row in xrange(start_row, end_row):
            # Exit when there are no more students
            if str(sheet.cell_value(row, 0)).strip() == '':
                break

            # Import new area and school if necessary.
            area = self.get_area(
                sheet.cell_value(row, colpos['region']),
                sheet.cell_value(row, colpos['location'])
            )
            school = self.get_school(area, sheet.cell_value(row, colpos['school']))
            # print area.location.country

            # Get donor.
            donor_id = int(sheet.cell_value(row, colpos['student_donor_id']))
            donor = Donor.objects.get(eep_id=donor_id)

            name = self.normalize_value(sheet.cell_value(row, colpos['student_name']))
            # If a student exists, update data except the name.  Else create it.
            try:
                s = Student.objects.get(name=name)
                old_school = s.school
            except:
                s = Student()
                s.name = name
                old_school = None

            # Disable school history recording.
            s.record_school_history = False


            sex = self.normalize_value(sheet.cell_value(row, colpos['sex'])) 
            s.sex = (Student.FEMALE if sex.find(u'女') >= 0 else Student.MALE)
            s.cls = self.normalize_value(sheet.cell_value(row, colpos['grade']))
            s.grad_yr = self.normalize_value(sheet.cell_value(row, colpos['graduation_year']))
            s.notes = self.normalize_value(sheet.cell_value(row, comment_pos))
            s.school = school

            try:
                s.save()
                Student.record_school_change(s, old_school, school, school_end_dt)

                # Assignment
                s.assign_to_donor(donor, sheet_info['yr'], sheet_info['season'])
            except:
                print sys.exc_info()
                print "Unable to save student: {}".format(row)




        print "Rows:", row

    def get_school(self, area, school_name):
        try:
            school = School.objects.get(name=school_name, area=area)
        except:
            school = School(name=school_name, area=area)
            school.save()

        return school

    def get_location(self, location_name):
        if location_name in [u'台灣', u'臺灣']:
            country = Location.TAIWAN
            location_name = u'臺灣'
        else:
            country = Location.CHINA

        try:
            location = Location.objects.get(name=location_name)
        except:
            location = Location(name=location_name, country=country)
            location.save()

        return location

    def get_area(self, location_name, area_name):
        location = self.get_location(location_name)

        try:
            area = Area.objects.get(name=area_name, location=location)
        except:
            area = Area(name=area_name, location=location)
            area.save()

        return area

    def get_donor(self, donor_id):
        return Donor.objects.get(eep_id=donor_id)

    def save_data(self, table, value):
        pass

    def import_donors(self, wb):
        colpos = {
            'eep_id': 0,
            'chi_name': 1,
            'eng_name': 2,
            'address': 3,
            'home_phone': 4,
            'cell_phone': 5,
            'office_phone': 6,
            'email': 7,
        }
        # self.stdout.write(fn)

        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE `donor_donor`")
        """
        Donor.objects.all().delete()

        # wb = xlrd.open_workbook(fn, on_demand=True, formatting_info=True)
        # Donor info
        sn = 23
        sheet = wb.sheet_by_index(sn)

        start_row = 0
        end_row = 3070
        end_col = 7
        for row in xrange(start_row, end_row):
            # Skip rows without a donor.
            if str(sheet.cell_value(row, 0)).strip() == '':
                continue

            donor = Donor()
            donor.eep_id = self.normalize_value(sheet.cell_value(row, colpos['eep_id']))
            donor.chi_name = self.normalize_value(sheet.cell_value(row, colpos['chi_name']))
            donor.eng_name = self.normalize_value(sheet.cell_value(row, colpos['eng_name']))
            donor.address = self.normalize_value(sheet.cell_value(row, colpos['address']))
            donor.home_phone = self.normalize_value(sheet.cell_value(row, colpos['home_phone']))
            donor.cell_value = self.normalize_value(sheet.cell_value(row, colpos['cell_phone']))
            donor.office_value = self.normalize_value(sheet.cell_value(row, colpos['office_phone']))
            donor.email = self.normalize_value(sheet.cell_value(row, colpos['email']))
            # if donor.eep_id >= 3000:
            #    donor.donation_country_limit = Location.CHINA

            try:
                donor.save()
            except:
                print "Unable to save row: {}".format(row)
                print sys.exc_info()[0]

            continue
            for col in xrange(0, end_col):
                # print (row, col)
                val = self.normalize_value(sheet.cell_value(row, col))

                # self.stdout.write(val)
                # print val

        wb.unload_sheet(sn)

    def normalize_value(self, val):
        if isinstance(val, float) or isinstance(val, int):
            val = int(val)
        if isinstance(val, str):
            val = val.encode('utf-8')

        return val

