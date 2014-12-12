# -*- coding: utf-8 -*-
import sys
import re
from datetime import datetime, date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from core.models import Season
from location.models import Location
from area.models import Area
from school.models import School
from donor.models import Donor, Donation
from student.models import Student, Assignment

import xlrd
from dateutil.parser import *

class Command(BaseCommand):
    DONOR_SHEET_NUMBER = 23
    DONATION_SECTION_COL_CNT = 8

    # args = '<poll_id poll_id ...>'
    help = 'Import EEP data.'

    def handle(self, *args, **options):
        fn = u'/Users/cc/Desktop/2014年秋季助學名冊.xlsm'
        fn = u'/Users/cc/Desktop/2014f.xls'
        # wb = xlrd.open_workbook(fn, on_demand=True, formatting_info=True)
        wb = xlrd.open_workbook(fn, on_demand=True)

        # Import donors.
        #self.import_donors(wb)

        """
        # For testing
        fn = u'/Users/cc/Desktop/donor_info.xls'
        wb = xlrd.open_workbook(fn, on_demand=True)
        self.DONOR_SHEET_NUMBER = 0
        """
        # Import donations.
        # self.import_donations(wb)


        # Import students and school assignments.
        # self.import_sheets(wb)

        self.import_students(wb, 17)

        sys.exit()

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

            print "Import students", i, name, info
            self.import_students(wb, i)

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
        # self.stdout.write("Import students...")
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

        # Determine if we need to alter colpos to older version.
        amt_title = sheet.cell_value(1, colpos['student_donor_donation_amount_local'])
        amt_title += sheet.cell_value(2, colpos['student_donor_donation_amount_local'])
        if amt_title.lower().find(u'amount') < 0:
            #print amt_title
            # print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            # Different version, adjust column positions.
            colpos.pop('donor_balance')
            adjust_list = ['student_name', 'sex', 'grade', 'graduation_year', 'student_donor_id',
                'student_donor_name', 'student_donor_donation_amount_local',
                'student_donor_donation_amount_us'
            ]
            for x in adjust_list:
                colpos[x] = colpos[x] - 1

            # Find correct comment column position
            s = colpos['student_donor_donation_amount_us']
            e = colpos['student_donor_donation_amount_us'] + 3
            for x in xrange(s, e):
                v = self.normalize_value(sheet.cell_value(1, x))
                if v.lower().find(u'comments') >= 0 or v == "":
                    # print "................ ", x
                    colpos['comment'] = colpos['comment_tw'] = x
                    break
            # print colpos

        """
        us_amt_title = self.normalize_value(
            sheet.cell_value(1, colpos['student_donor_donation_amount_us'])
        ).strip()
        if us_amt_title == u"USD":
            # print "YES....."
            pass
        """

        if sheet_info['country'] == Location.TAIWAN:
            comment_pos = colpos['comment_tw']
        else:
            comment_pos = colpos['comment'] 

        if sheet_info['season'] == Season.SPRING:
            dt = '1/1/{}'
        else:
            dt = '6/1/{}'
        school_end_dt = datetime.strptime(dt.format(sheet_info['yr']), '%m/%d/%Y')
        school_end_dt -= timedelta(seconds=1)
        # print school_end_dt
        # print sheet.number, sheet.name, sheet_info

        # Import each student, school assignment, donor assignment.
        start_row = 3
        end_row = 3070
        for row in xrange(start_row, end_row):
            """Exit when there are no more students by checking for empty value in the
            first and 2nd column.
            """
            if (
                unicode(self.normalize_value(sheet.cell_value(row, 0))).strip() == '' and
                unicode(self.normalize_value(sheet.cell_value(row + 1, 0))).strip() == ''
            ):
                break

            dm = self.normalize_value(sheet.cell_value(
                row, colpos['student_donor_donation_amount_us'])
            )

            # Import new area and school if necessary.
            area = self.get_area(
                sheet.cell_value(row, colpos['region']),
                sheet.cell_value(row, colpos['location'])
            )
            school = self.get_school(area, sheet.cell_value(row, colpos['school']))
            # print area.location.country

            # Get donor.
            donor_id = int(sheet.cell_value(row, colpos['student_donor_id']))
            donor = self.get_donor(donor_id)

            # If a student exists, update data except the name.  Else create it.
            try:
                name = self.normalize_value(sheet.cell_value(row, colpos['student_name']))
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
                assignment = s.assign_to_donor(
                    donor,
                    sheet_info['yr'],
                    sheet_info['season'],
                    self.normalize_value(sheet.cell_value(
                        row, colpos['student_donor_donation_amount_us'])
                    )
                )
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
        return Donor.objects.get(eep_id=int(donor_id))

    def save_data(self, table, value):
        pass

    def process_donation_section(self, wb, sheet, donor, row, section_start_col):
        colpos = {
            'donation_dt': 0,
            'notes': 1,
            # Amount is in US dollar. 總捐款額扣10元/年/人
            'donation_amount': 2,
            'receipt': 3,
            #'amount_used_by_china': 4,
            #'amount_used_by_taiwan': 5,
            #'amount_balance': 6,
            #'blank_col': 7,
        }
        ssc = section_start_col
        require_attention = False

        end_section_col = section_start_col + self.DONATION_SECTION_COL_CNT - 1
        section_info = u'{}{}'.format(
            sheet.cell_value(0, end_section_col),
            sheet.cell_value(1, end_section_col)
        )
        info = self.get_info_from_sheet_name(section_info)
        # print section_info, info

        amount = self.normalize_value(
            sheet.cell_value(row, ssc + colpos['donation_amount'])
        )
        if amount <= 0 or amount is None or amount == "":
            return

        notes = self.normalize_value(sheet.cell_value(row, ssc + colpos['notes']))
        # Donation date check.
        donation_dt = sheet.cell_value(row, ssc + colpos['donation_dt'])
        if isinstance(donation_dt, float):
            donation_dt = datetime(*xlrd.xldate_as_tuple(donation_dt, wb.datemode))
            # print donation_dt
        else:
            try:
                parsed_donation_dt = parse(donation_dt)
                donation_dt = parsed_donation_dt
                # print "parsed: ", donation_dt 
            except:
                pass

        # Invalid donation date.  Save value in notes, set attention_required and set the donation_dt to null
        if not isinstance(donation_dt, datetime):
            """
            print u"Incorrect date format: donor {} row {} season: {}{} ssc {} format: {}".format(
                donor, row, info['yr'], info['season'], ssc, donation_dt
            )
            """
            notes += u" Auto Notes: Invalid Date Values: {}".format(donation_dt)
            donation_dt = None
            require_attention = True

        # Create donation.
        donation = Donation(
            donor=donor,
            dt=donation_dt,
            amount=amount,
            receipt_number=self.normalize_value(sheet.cell_value(row, ssc + colpos['receipt'])),
            notes=notes,
            yr=info['yr'],
            season=info['season'],
            require_attention=require_attention
        )
        try:
            donation.save()
        except:
            print u"Error importing donation: {}".format(donation)
            print sys.exc_info()
        #if donation.require_attention:
        #    print "==", donation

    def import_donations(self, wb):
        self.stdout.write("Import donations...")
        sheet = wb.sheet_by_index(self.DONOR_SHEET_NUMBER)
        
        # Get all donation section starting columns.
        first_section_col = 9
        section_cols = [i for i in xrange(
            first_section_col, sheet.ncols, self.DONATION_SECTION_COL_CNT
        )]

        Donation.objects.all().delete() 

        start_row = 0
        end_row = 3070
        # end_row = 10
        # Import donor donations.
        for row in xrange(start_row, end_row):
            # Skip rows without a donor.
            try:
                cv = sheet.cell_value(row, 0)
                if str(sheet.cell_value(row, 0)).strip() == '':
                    continue
            except:
                print "Error access row ", (row + 1) 
                break

            # Import donations for the subject donor.
            for col in section_cols:
                # print "row:", row, "col:", col,
                eep_id = self.normalize_value(sheet.cell_value(row, 0))
                donor = self.get_donor(eep_id)
                self.process_donation_section(wb, sheet, donor, row, col)

        # wb.unload_sheet(self.DONOR_SHEET_NUMBER)

    def import_donors(self, wb):
        self.stdout.write("Import donors...")
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

        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE `donor_donor`")
        """
        # Donor.objects.all().delete()

        # Donor info
        sheet = wb.sheet_by_index(self.DONOR_SHEET_NUMBER)

        start_row = 0
        end_row = 3070
        end_col = 7
        for row in xrange(start_row, end_row):
            # Skip rows without a donor.
            if str(sheet.cell_value(row, 0)).strip() == '':
                continue

            eep_id = int(self.normalize_value(sheet.cell_value(row, colpos['eep_id'])))

            # See if donor exists.  If it does, update data.
            try:
                donor = self.get_donor(eep_id)
            except:
                # Donor does not exist.  Create it.
                donor = Donor()
                # print sys.exc_info()
                # print "eep_id ", eep_id, " does not exist"

            # Create donor
            try:
                donor.eep_id = eep_id
                donor.chi_name = self.normalize_value(sheet.cell_value(row, colpos['chi_name']))
                donor.eng_name = self.normalize_value(sheet.cell_value(row, colpos['eng_name']))
                donor.address = self.normalize_value(sheet.cell_value(row, colpos['address']))
                donor.home_phone = self.normalize_value(sheet.cell_value(row, colpos['home_phone']))
                donor.cell_value = self.normalize_value(sheet.cell_value(row, colpos['cell_phone']))
                donor.office_value = self.normalize_value(sheet.cell_value(row, colpos['office_phone']))
                donor.email = self.normalize_value(sheet.cell_value(row, colpos['email']))
                donor.save()
            except IntegrityError as e:
                print "IntegrityError @ row {}: {}".format(row, e.__cause__)
                donor.chi_name = donor.chi_name + u" (2)"
                donor.save()
                print u"Renamed donor chi_name to {}".format(donor.chi_name)
            except:
                print "Unable to save row: {}".format(row)
                print sys.exc_info()[0]

        # wb.unload_sheet(self.DONOR_SHEET_NUMBER)

    def normalize_value(self, val):
        if isinstance(val, float) or isinstance(val, int):
            val = int(val)
        elif isinstance(val, str):
            val = val.encode('utf-8').strip()
        elif isinstance(val, unicode):
            val = val.strip()

        return val

