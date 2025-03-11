from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Penalty, SecretReport, Course, IdealEmployee, PoliceDayHonoredEmployee, EmployeeAttendance, Division, Governorate, AcademicQualification, EmployeeVacation, CourseName, Employee,DepartmentsAndSections,EmploymentHistory,Sections
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django import forms
from django.utils import timezone
from django.utils.http import urlencode
from django.urls import reverse
from rangefilter.filters import (
    DateRangeFilterBuilder,
    DateTimeRangeFilterBuilder,
    NumericRangeFilterBuilder,
    DateRangeQuickSelectListFilterBuilder,
)
from django.core.exceptions import ValidationError
import re
from django.db import models
from datetime import date, datetime
from django.db import connection
from django.urls import path
from django.http import HttpResponseRedirect
from .widgets import AdminImageWidget  # Ensure the widget is correctly imported
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

# Register your models here.
class AcademicQualificationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class EmployeeVacationAdminForm(forms.ModelForm):
    class Meta:
        model = EmployeeVacation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['place_text'].widget.attrs['style'] = 'display: none;'
        self.fields['place_link'].widget.attrs['style'] = 'display: none;'
        self.fields['section_place_link'].widget.attrs['style'] = 'display: none;'

class EmployeeVacationAdmin(admin.ModelAdmin):
    form = EmployeeVacationAdminForm
    list_display = ('employee', 'type', 'fromDate', 'toDate', 'days', 'remainingBalance', 'place_text', 'place_link','section_place_link')
    list_filter = (
        'type',
        ("fromDate", DateRangeFilterBuilder()),
        ("toDate", DateRangeFilterBuilder()),
    )
    search_fields = ('employee__firstName',)

    class Media:
        js = ('admin/js/employee_vacation.js',)  # Add this JavaScript file to control field visibility

class IdealEmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date')
    list_filter = (
        ("date", DateRangeFilterBuilder()),
    )
    search_fields = ('employee__firstName',)

class PoliceDayHonoredEmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date')
    list_filter = ('date',)
    search_fields = ('employee__firstName',)
    list_filter = (
        ("date", DateRangeFilterBuilder()),
    )

class EmployeeAttendanceAdminForm(forms.ModelForm):
    class Meta:
        model = EmployeeAttendance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['place_text'].widget.attrs['style'] = 'display: none;'
        self.fields['place_link'].widget.attrs['style'] = 'display: none;'
        self.fields['section_place_link'].widget.attrs['style'] = 'display: none;'

class EmployeeAttendanceAdmin(admin.ModelAdmin):
    form = EmployeeAttendanceAdminForm
    today = timezone.now().date()
    list_display = ('employee', 'status', 'dayDate')
    search_fields = ('employee__firstName',)
    change_list_template = "admin/employee_attendance_change_list.html"  # Custom template
    list_filter = (("dayDate", DateRangeFilterBuilder()),)  # Standard date filter
    class Media:
        js = ('admin/js/employee_vacation.js',)  # Add this JavaScript file to control field visibility

    # Override changelist_view to apply the default date filter
    def changelist_view(self, request, extra_context=None):
        """Redirects to apply default filter for today's date if no filter is set."""
        if not request.GET:
            return redirect(f"{request.path}?dayDate__range__gte={self.today}&dayDate__range__lte={self.today}")
        return super().changelist_view(request, extra_context)
    # Custom action view
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-attendance/', self.add_attendance_view, name='add_attendance'),
        ]
        return custom_urls + urls

    def add_attendance_view(self, request):
            """Handle the custom action triggered by the button."""
            today = timezone.now().date()
            employees = Employee.objects.all()  # Retrieve all employees
            created_count = 0
            skipped_count = 0

            # Define STATUSES with Arabic and English mappings
            STATUSES = {
                "P": ["بالعمل", "Present"],  # present
                "S": ["مرضي", "Sick"],  # sick
                "C": ["عارضة", "Casual"],  # casual
                "IMS": ["مأمورية داخلية", "Inside Mission"],  # mission
                "OMS": ["مأمورية خارجية", "Outside Mission"],  # mission
                "F": ["دورة تدريبية", "Course"],  # training
                "A": ["دوري", "Annual"],  # annual
                "M": ["غياب", "Missing"],  # missing
                "O": ["راحة", "Off"],  # off day
                "P65%": ["بالعمل خمسة وستون", "Partial"],  # partial present
                "l": ["اجازة بدون مرتب", "Unpaid Leave"],  # leave without pay
            }

            # Create a reverse mapping (Arabic/English name to status code)
            arabic_to_status = {name: code for code, names in STATUSES.items() for name in names}

            for employee in employees:
                # Check if the employee has a vacation record on the same day
                vacations = EmployeeVacation.objects.filter(
                    employee=employee, fromDate__lte=today, toDate__gte=today
                )

                if vacations.exists():
                    for vacation in vacations:
                        vacation_type = getattr(vacation, "type", None)
                        vacation_status = arabic_to_status.get(vacation_type, "P")
                        print(vacation_status)
                        if not vacation_status:
                            print(f"Unmapped vacation type: {vacation_type} for employee {employee}")
                            skipped_count += 1
                            continue
                        if vacation_status== "OMS":
                            place_text = getattr(vacation, "place_text", None)
                            defaults= {'status': vacation_status,'place_text':place_text}
                        elif vacation_status== "IMS":
                            place_link = getattr(vacation, "place_link", None)
                            section_place_link = getattr(vacation, "section_place_link", None)
                            defaults= {'status': vacation_status,'place_link':place_link,'section_place_link':section_place_link}
                        else:
                            defaults= {'status': vacation_status}
                        # print(defaults)
                        # Create attendance with the vacation's status
                        attendance, created = EmployeeAttendance.objects.get_or_create(
                            employee=employee,
                            dayDate=today,
                            defaults=defaults
                        )
                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1
                    continue

                # Check if the employee already has an attendance record with vacation/leave status
                if EmployeeAttendance.objects.filter(employee=employee, dayDate=today, status__in=['A', 'l']).exists():
                    skipped_count += 1
                    continue

                # Default status
                default_status = "P"

                # Add attendance record if it doesn't exist
                attendance, created = EmployeeAttendance.objects.get_or_create(
                    employee=employee,
                    dayDate=today,
                    defaults={'status': default_status}
                )

                if created:
                    created_count += 1

            # Notify the admin about the result
            self.message_user(
                request,
                f"تم إضافة عدد {created_count} موظفين. بأستثناء عدد {skipped_count} موظفين بسبب الإجازات أو الأخطاء."
            )
            return HttpResponseRedirect("../")

class CourseInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CourseInlineForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.Select(choices=[(course_name.name, course_name.name) for course_name in CourseName.objects.all()])
    
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'certificateObtained': forms.RadioSelect(choices=[(True, 'نعم'), (False, 'لا')]),
        }
        
class CourseInline(admin.TabularInline):
    model = Course
    form = CourseInlineForm
    extra = 0
    show_change_link = True
    
class PenaltyInline(admin.TabularInline):
    model = Penalty
    extra = 0
    show_change_link = True
    
class SecretReportInline(admin.TabularInline):
    model = SecretReport
    extra = 0
    show_change_link = True

CustomUser = get_user_model()

class CustomUserForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'  # Ensure all fields are included

class CustomUserAdmin(UserAdmin):
    form = CustomUserForm  # Use the custom form
    list_display = ('username', 'email', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')


class DivisionInline(admin.TabularInline):
    model = Division
    extra = 1

class GovernorateAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [DivisionInline]

class SectionsInline(admin.TabularInline):
    model = Sections
    extra = 1

class DepartmentsAndSectionsAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [SectionsInline]

class CourseNameAdmin(admin.ModelAdmin):
    search_fields = ('name',)

############################## Emp #######################
class EmployeeChangeForm(forms.ModelForm):
    birthGovernorateFF = forms.ModelChoiceField(queryset=Governorate.objects.all(), required=False, label=_('Birth Governorate'))
    birthDivisionFF = forms.ModelChoiceField(queryset=Division.objects.none(), required=False, label=_("Birth Division"))
    
    addressGovernorateFF = forms.ModelChoiceField(queryset=Governorate.objects.all(), required=False, label=_('Address Governorate'))
    addressDivisionFF = forms.ModelChoiceField(queryset=Division.objects.none(), required=False, label=_("Address Division"))
    
    academicQualificationsFF = forms.ModelChoiceField(queryset=AcademicQualification.objects.all(), required=False, label=_("Academic Qualifications"))
    currentEmployerFF = forms.ModelChoiceField(queryset=DepartmentsAndSections.objects.all(), required=False, label=_("Departments"))
    currentEmployerSectionFF = forms.ModelChoiceField(queryset=Sections.objects.none(), required=False, label=_("Sections"))  # Initially empty

    class Meta():
        model = Employee
        fields = '__all__'
        widgets = {
            'gender': forms.RadioSelect,
            'religion': forms.RadioSelect,
            'previousHaj': forms.RadioSelect(choices=[(True, 'نعم'), (False, 'لا')]),
            'solidarityFund': forms.RadioSelect(choices=[(True, 'نعم'), (False, 'لا')]),
            'stakeholderFund': forms.RadioSelect(choices=[(True, 'نعم'), (False, 'لا')]),
            'insuranceUmbrella': forms.RadioSelect(choices=[(True, 'نعم'), (False, 'لا')]),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['firstName'].required = True
        self.fields['secondName'].required = True
        self.fields['thirdName'].required = True
        self.fields['lastName'].required = True
        self.fields['birthDate'].required = True
        self.fields['insuranceNumber'].required = True
        self.fields['healthInsuranceNumber'].required = True
        self.fields['academicQualificationsFF'].required = True
        self.fields['jobFamily'].required = True
        self.fields['graduationYear'].required = True
        self.fields['employmentDate'].required = True
        self.fields['decisionNumber'].required = True
        self.fields['militaryStatus'].required = True
        self.fields['jobStartDate'].required = True
        self.fields['currentRank'].required = True
        self.fields['currentEmployer'].required = True
        self.fields['currentEmployerSection'].required = True
        self.fields['previousHajDate'].required = True
        self.fields['retirementDate'].required = True
        self.fields['solidarityFundDate'].required = True
        self.fields['stakeholderFundDate'].required = True
        self.fields['insuranceUmbrellaDate'].required = True
        self.fields['currentEmploymentStartDate'].required = True

        if 'birthGovernorateFF' in self.data:
            try:
                birthGovernorateFF_id = int(self.data.get('birthGovernorateFF'))
                self.fields['birthDivisionFF'].queryset = Division.objects.filter(governorate=birthGovernorateFF_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Town queryset
        elif self.instance.pk and self.instance.birthGovernorate:
            gov = Governorate.objects.filter(name=self.instance.birthGovernorate).first()
            if gov:
                self.fields['birthDivisionFF'].queryset = Division.objects.filter(governorate=gov.id).order_by('name')
                
        if 'addressGovernorateFF' in self.data:
            try:
                addressGovernorateFF_id = int(self.data.get('addressGovernorateFF'))
                self.fields['addressDivisionFF'].queryset = Division.objects.filter(governorate=addressGovernorateFF_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Town queryset
        elif self.instance.pk and self.instance.addressGovernorate:
            gov = Governorate.objects.filter(name=self.instance.addressGovernorate).first()
            if gov:
                self.fields['addressDivisionFF'].queryset = Division.objects.filter(governorate=gov.id).order_by('name')

        # Filtering Sections based on selected currentEmployer
        if 'currentEmployerFF' in self.data:
            try:
                currentEmployer_id = int(self.data.get('currentEmployerFF'))
                self.fields['currentEmployerSectionFF'].queryset = Sections.objects.filter(currentEmployer=currentEmployer_id)
            except (ValueError, TypeError):
                pass  
        elif self.instance.pk and self.instance.currentEmployer:
            self.fields['currentEmployerSectionFF'].queryset = Sections.objects.filter(department_id=self.instance.currentEmployer)
    
    def save_model(self, request, obj, form, change):
        instance = super().save(commit=False)

        # Required field checks
        missing_fields = []

        if not instance.birthGovernorate:
            missing_fields.append(str(_('Birth Governorate')))
        
        if not instance.addressGovernorate:
            missing_fields.append(str(_('Address Governorate')))
        
        if not instance.addressDivision:
            missing_fields.append(str(_('Address Division')))
        
        if not instance.birthDivision:
            missing_fields.append(str(_('Birth Division')))

        # Show popup message if any required field is missing
        if missing_fields:
            msg= f"Please fill in the missing fields: {', '.join(missing_fields)}"
            messages.warning(message=msg,request=request)

        address_governorate_ff = self.cleaned_data.get('addressGovernorateFF')
        if address_governorate_ff:
            instance.addressGovernorate = address_governorate_ff.name  # Ensure it's saved

        addressDivision_ff = self.cleaned_data.get('addressDivisionFF')
        if address_governorate_ff:
            instance.addressDivision = addressDivision_ff.name  # Ensure it's saved
        
        BirthDivision_ff = self.cleaned_data.get('academicQualificationsFF')
        if BirthDivision_ff:
            instance.academicQualifications = BirthDivision_ff.name  # Ensure it's saved
        # Handle governorate assignment safely
        birth_governorate_ff = self.cleaned_data.get('birthGovernorateFF')

        academicQualificationsFF = self.cleaned_data.get('birthDivisionFF')
        if academicQualificationsFF:
            instance.birthDivision = academicQualificationsFF.name  # Ensure it's saved
        # Handle governorate assignment safely
        birth_governorate_ff = self.cleaned_data.get('birthGovernorateFF')

        if birth_governorate_ff:
            instance.birthGovernorate = birth_governorate_ff
            governorate_name = birth_governorate_ff.name
        else:
            governorate_name = instance.birthGovernorate.name if instance.birthGovernorate else None

        # Validate National ID
        nationalId = self.cleaned_data.get('nationalId', '')
        birthDate = self.cleaned_data.get('birthDate')
        gender = self.cleaned_data.get('gender')

        validation_result = self._validate_national_id(nationalId, birthDate, gender, governorate_name)

        if validation_result == 6:
            raise ValidationError({'nationalId': 'المحافظة غير مطابقة للرقم القومي'})
        elif validation_result == 7:
            raise ValidationError({'nationalId': 'المحافظة غير موجودة في قاعدة البيانات'})
        elif validation_result == 5:
            raise ValidationError({'nationalId': 'النوع غير مطايق لرقم البطاقة'})
        elif validation_result != True:
            raise ValidationError({'nationalId': 'الرقم القومي غير صحيح'})

        super().save_model(request, obj, form, change)

        return instance


    def _validate_national_id(self, nationalId, birthDate, gender, governorate):
        """
        Validates the national ID according to Egyptian rules.
        """
        try:
            if not nationalId or not isinstance(nationalId, str) or len(nationalId) < 14:
                return 2  # National ID must be 14 digits

            # National ID format validation using regex
            nationalIdRegex = r'^([2-3]{1})([0-9]{2})(0[1-9]|1[012])(0[1-9]|[1-2][0-9]|3[0-1])(0[1-4]|[1-2][1-9]|3[1-5]|88)[0-9]{3}([0-9]{1})[0-9]{1}$'
            if not re.fullmatch(nationalIdRegex, nationalId):
                return 3  # Invalid format

            # Validate birth date from National ID
            datePart = nationalId[1:7]  # YYMMDD
            datePartString = f"{datePart[0:2]}-{datePart[2:4]}-{datePart[4:6]}"
            datePartDate = datetime.strptime(datePartString, "%y-%m-%d").date()
            if birthDate != datePartDate:
                return 4  # Birth date does not match

            # Validate gender from National ID (13th digit)
            gender_digit = int(nationalId[12])
            expected_gender = "Female" if gender_digit % 2 == 0 else "Male"
            
            if gender != expected_gender:
                return 5  # Gender does not match

            # Validate governorate from National ID
            governoratePare = int(nationalId[7:9])

            if not governorate:
                print("Skipping governorate validation because it's missing.")
                return True  # Don't fail validation if governorate is missing

            governorate_instance = Governorate.objects.filter(national_governorate_id=governoratePare).first()

            if governorate_instance:
                governorate_name_db = governorate_instance.name
                if governorate_name_db != governorate:
                    return 6  # Governorate does not match
            else:
                return 7  # Governorate not found in database

            return True
        except Exception as e:
            print(f"Validation Error: {e}")
            return 8  # Unexpected error

class EmploymentHistoryInline(admin.TabularInline):
    """ Display previous employment history as a read-only table inside Employee Admin """
    model = EmploymentHistory
    extra = 0  # Do not show extra empty rows
    # readonly_fields = ('employer_name', 'start_date', 'end_date')  # Make all fields read-only
    # can_delete = False  # Prevent deletion from the admin panel
    # max_num = 0  # Prevent adding new records manually from the admin panel

class EmployeeAdmin(admin.ModelAdmin):
    list_filter = ()
    model = Employee
    form = EmployeeChangeForm
    inlines = [EmploymentHistoryInline,CourseInline, PenaltyInline, SecretReportInline]
    readonly_fields = (
    'periodicVacations', 'casualVacations', 'birthGovernorate',
    'birthDivision', 'academicQualifications',
    )

    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }
    def number_of_penalties(self, obj):
        return obj.penalties.count()

    number_of_penalties.short_description = _('Penalties')
    list_display = ('firstName', 'secondName', 'number_of_penalties',)

    fieldsets = (
        (
            _('Personal info'), {
                'classes': ('main-form',),
                'fields': (
                    ('employee_image'),
                    ('firstName', 'secondName', 'thirdName', 'lastName'), 
                    ('birthGovernorateFF', 'birthDivisionFF'),
                    ('birthGovernorate', 'birthDivision'),
                    ('nationalId', 'religion', 'birthDate', 'insuranceNumber', 'healthInsuranceNumber','gender'),
                    ('addressGovernorateFF', 'addressDivisionFF'),
                    ('addressGovernorate', 'addressDivision'),
                    ('previousHaj', 'previousHajDate'),
                    ('academicQualificationsFF', 'academicQualifications', 'jobFamily', 'graduationYear', 'militaryStatus'),
                    ('solidarityFund', 'solidarityFundDate'), 
                    ('stakeholderFund', 'stakeholderFundDate'), 
                    ('insuranceUmbrella', 'insuranceUmbrellaDate')
                )
            }
        ),
        (
            _('Employment info'), {
                'fields': (
                    ('employmentDate', 'decisionNumber', 'jobStartDate', 'currentRank'),
                    # ('previousEmployer', 'previousEmploymentStartDate', 'previousEmploymentEndDate'),
                    ('currentEmployer','currentEmployerSection','currentEmploymentStartDate'),
                    ('retirementDate', 'periodicVacations', 'casualVacations')
                ),
                
            }
        ),
    )
    

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = super().get_fieldsets(request, obj)
    #     if not obj or request.user.is_superuser:
    #         return fieldsets

    #     # Exclude specific fields for non-superusers
    #     exclude_fields = ('groups', 'user_permissions')
    #     return [
    #         (fieldset[0], {'fields': tuple(field for field in fieldset[1]['fields'] if field not in exclude_fields)})
    #         for fieldset in fieldsets
    #     ]


    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('periodicVacations', 'casualVacations', 'birthGovernorate', 'birthDivision', 'addressGovernorate', 'addressDivision', 'academicQualifications')  # Return an empty tuple for superusers to have no read-only fields
        if not obj:  # When creating a new user, no fields are read-only
            return self.readonly_fields
        if request.user == obj:
            return [field.name for field in self.model._meta.fields if field.name not in ['firstName']]
        return self.readonly_fields

    def has_view_permission(self, request, obj=None):
        if obj is not None and request.user == obj:
            return True
        return super().has_view_permission(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset  # Superuser can see all users
        return queryset.filter(pk=request.user.pk)  # Normal user can only see their own record
    
    class Media:
        css = {
            'all': ('base/custom_admin.css',),
        }
        js = ('base/js/admin_custom.js','base/js/admin_dynamic_filters.js',)

# admin.site.unregister(CustomUser)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(IdealEmployee, IdealEmployeeAdmin)
admin.site.register(PoliceDayHonoredEmployee, PoliceDayHonoredEmployeeAdmin)
admin.site.register(EmployeeAttendance, EmployeeAttendanceAdmin)
admin.site.register(Governorate, GovernorateAdmin)
admin.site.register(DepartmentsAndSections,DepartmentsAndSectionsAdmin)
admin.site.register(AcademicQualification, AcademicQualificationAdmin)
admin.site.register(EmployeeVacation, EmployeeVacationAdmin)
admin.site.register(CourseName, CourseNameAdmin)
admin.site.unregister(Group)