from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Penalty, SecretReport,
    Course, IdealEmployee, PoliceDayHonoredEmployee,
    EmployeeAttendance, Division, Governorate,
    AcademicQualification, EmployeeVacation, CourseName,
    Employee,DepartmentsAndSections,EmploymentHistory,Sections
    )
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django import forms
from django.utils import timezone
from rangefilter.filters import DateRangeFilterBuilder
from django.core.exceptions import ValidationError
import re
from django.db import models
from datetime import datetime
from django.urls import path
from django.http import HttpResponseRedirect
from .widgets import AdminImageWidget
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

class AcademicQualificationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class EmployeeVacationAdminForm(forms.ModelForm):
    class Meta:
        model = EmployeeVacation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        
        if employee and not employee.is_active:
            raise ValidationError('لا يمكن إضافة إجازة لموظف غير نشط.')
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

class EmployeeVacationAdmin(admin.ModelAdmin):
    form = EmployeeVacationAdminForm
    list_display = ('employee', 'type', 'fromDate', 'toDate', 'days', 'remainingBalance')
    list_filter = (
        'type',
        ("fromDate", DateRangeFilterBuilder()),
        ("toDate", DateRangeFilterBuilder()),
    )
    search_fields = ('employee__firstName',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def save_model(self, request, obj, form, change):
        if obj.employee and not obj.employee.is_active:
            from django.contrib import messages
            messages.error(request, 'لا يمكن إضافة إجازة لموظف غير نشط.')
            return  # Don't save
        super().save_model(request, obj, form, change)

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

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        
        if employee and not employee.is_active:
            raise ValidationError('لا يمكن إضافة حضور لموظف غير نشط.')
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

class EmployeeAttendanceAdmin(admin.ModelAdmin):
    form = EmployeeAttendanceAdminForm
    today = timezone.now().date()
    list_display = ('employee', 'status', 'dayDate')
    search_fields = ('employee__firstName',)
    change_list_template = "admin/employee_attendance_change_list.html"  # Custom template
    list_filter = (("dayDate", DateRangeFilterBuilder()),)  # Standard date filter

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def save_model(self, request, obj, form, change):
        if obj.employee and not obj.employee.is_active:
            from django.contrib import messages
            messages.error(request, 'لا يمكن إضافة حضور لموظف غير نشط.')
            return  # Don't save
        super().save_model(request, obj, form, change)

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
                        # if vacation_status== "OMS":
                        #     place_text = getattr(vacation, "place_text", None)
                        #     defaults= {'status': vacation_status,'place_text':place_text}
                        # elif vacation_status== "IMS":
                        #     place_link = getattr(vacation, "place_link", None)
                        #     section_place_link = getattr(vacation, "section_place_link", None)
                        #     defaults= {'status': vacation_status,'place_link':place_link,'section_place_link':section_place_link}
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
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # تحديد الحقول المطلوبة
        required_fields = [
            'firstName', 'secondName', 'thirdName', 'lastName',
            'birthDate', 'insuranceNumber', 'healthInsuranceNumber',
            'jobFamily', 'graduationYear', 'employmentDate',
            'decisionNumber', 'militaryStatus', 'jobStartDate',
            'currentRank', 'currentEmployer', 'currentEmployerSection',
            'retirementDate', 'currentEmploymentStartDate'
        ]
        
        for field in required_fields:
            self.fields[field].required = True
        # checkbox logic - based on initial data or form data
        data = self.data or self.initial
        if data.get('previousHaj') in ['True', True, 'on', '1']:
            self.fields['previousHajDate'].required = True
        if data.get('solidarityFund') in ['True', True, 'on', '1']:
            self.fields['solidarityFundDate'].required = True
        if data.get('stakeholderFund') in ['True', True, 'on', '1']:
            self.fields['stakeholderFundDate'].required = True
        if data.get('insuranceUmbrella') in ['True', True, 'on', '1']:
            self.fields['insuranceUmbrellaDate'].required = True
        # تجهيز queryset الخاص بالتقسيمات address/birth حسب المحافظات
        def set_division_queryset(field_name, gov_field_name):
            gov_obj = None

            # إذا كان هناك قيمة في الـ request (POST)
            if gov_field_name in self.data:
                try:
                    gov_id = int(self.data.get(gov_field_name))
                    gov_obj = Governorate.objects.get(pk=gov_id)
                except (ValueError, Governorate.DoesNotExist):
                    gov_obj = None

            # إذا كان في instance موجود
            elif self.instance.pk:
                gov_name = getattr(self.instance, gov_field_name.replace("FF", ""), "")
                gov_obj = Governorate.objects.filter(name=gov_name).first()

            # ضبط الـ queryset
            if gov_obj:
                self.fields[field_name].queryset = Division.objects.filter(governorate=gov_obj).order_by("name")
            else:
                self.fields[field_name].queryset = Division.objects.none()

        set_division_queryset('birthDivisionFF', 'birthGovernorateFF')
        set_division_queryset('addressDivisionFF', 'addressGovernorateFF')

        # تجهيز الأقسام الخاصة بالجهة الحالية
        if 'currentEmployerFF' in self.data:
            try:
                employer_id = int(self.data.get('currentEmployerFF'))
                self.fields['currentEmployerSectionFF'].queryset = Sections.objects.filter(currentEmployer=employer_id)
            except (ValueError, TypeError):
                self.fields['currentEmployerSectionFF'].queryset = Sections.objects.none()
        elif self.instance.pk and self.instance.currentEmployer:
            self.fields['currentEmployerSectionFF'].queryset = Sections.objects.filter(department_id=self.instance.currentEmployer)
    def save(self, commit=True):
        instance = super().save(commit=False)
        request = self.request
        # تحقق من الحقول المطلوبة
        missing_fields = []

        if not self.cleaned_data.get('birthGovernorateFF'):
            missing_fields.append(str(_('Birth Governorate')))
        if not self.cleaned_data.get('addressGovernorateFF'):
            missing_fields.append(str(_('Address Governorate')))
        if not self.cleaned_data.get('addressDivisionFF'):
            missing_fields.append(str(_('Address Division')))
        if not self.cleaned_data.get('birthDivisionFF'):
            missing_fields.append(str(_('Birth Division')))

        # if missing_fields and self.request:
        #     messages.warning(self.request, f"يرجى ملء الحقول التالية: {', '.join(missing_fields)}")
        #     raise ValidationError("الرجاء استكمال البيانات المطلوبة.")

        # ✅ اسناد الأسماء بدل الـ object الكامل
        gov = self.cleaned_data.get('addressGovernorateFF')
        instance.addressGovernorate = gov.name if gov else instance.addressGovernorate

        gov2 = self.cleaned_data.get('birthGovernorateFF')
        instance.birthGovernorate = gov2 if gov2 else instance.birthGovernorate

        division = self.cleaned_data.get('addressDivisionFF')
        instance.addressDivision = division.name if division else instance.addressDivision

        birth_div = self.cleaned_data.get('birthDivisionFF')
        instance.birthDivision = birth_div.name if birth_div else instance.birthDivision

        qual = self.cleaned_data.get('academicQualificationsFF')
        instance.academicQualifications = qual.name if qual else instance.academicQualifications

        # التحقق من الرقم القومي
        nationalId = self.cleaned_data.get('nationalId', '')
        birthDate = self.cleaned_data.get('birthDate')
        gender = self.cleaned_data.get('gender')
        governorate = gov2.name if gov2 else None

        # print(f"nationalId:{nationalId}, birthDate:{birthDate}, gender:{gender}, governorate:{governorate}")
        validation_result = self._validate_national_id(nationalId, birthDate, gender, governorate)
        # print(f"validation_result: {validation_result}")

        if validation_result == 6:
            messages.error(request, 'المحافظة غير مطابقة للرقم القومي')
            return instance
        elif validation_result == 7:
            messages.error(request, 'المحافظة غير موجودة في قاعدة البيانات')
            return instance
        elif validation_result == 5:
            messages.error(request, 'النوع غير مطابق لرقم البطاقة')
            return instance
        elif validation_result != True:
            messages.error(request, 'الرقم القومي غير صحيح')
            return instance

        if commit and not self.errors:
            instance.save()

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
                # print("Skipping governorate validation because it's missing.")
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

class EmployeeVacationInlineForm(forms.ModelForm):
    class Meta:
        model = EmployeeVacation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.required = False

        if self.instance.pk:
            readonly_fields = ['fromDate', 'toDate', 'type', 'days', 'remainingBalance']
            for field in readonly_fields:
                if field in self.fields:
                    self.fields[field].disabled = True
                    value = self.initial.get(field) or getattr(self.instance, field, None)
                    # add hidden version of the field
                    self.fields[f'{field}_hidden'] = forms.CharField(
                        initial=value.pk if hasattr(value, 'pk') else value,
                        widget=forms.HiddenInput(),
                        required=False
                    )

    def clean(self):
        cleaned_data = super().clean()

        # Restore hidden values for disabled fields
        readonly_fields = ['fromDate', 'toDate', 'type', 'days', 'remainingBalance']
        for field in readonly_fields:
            hidden_name = f'{field}_hidden'
            if hidden_name in self.data:
                val = self.data.get(self.add_prefix(hidden_name))
                if field == 'type' and val:
                    try:
                        # Convert ID to actual object
                        val = self.fields['type'].queryset.get(pk=val)
                    except:
                        val = None
                cleaned_data[field] = val

        return cleaned_data





class EmployeeVacationInline(admin.TabularInline):
    model = EmployeeVacation
    form = EmployeeVacationInlineForm
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        original_form_init = formset.form.__init__

        def custom_form_init(form_self, *args, **kwargs):
            original_form_init(form_self, *args, **kwargs)
            if not form_self.instance.pk:
                for field in form_self.fields.values():
                    field.disabled = False
                    field.widget.attrs.pop('disabled', None)

        formset.form.__init__ = custom_form_init
        return formset

class EmployeeAttendanceInlineForm(forms.ModelForm):
    class Meta:
        model = EmployeeAttendance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ اجعل كل الحقول غير مطلوبة لتفادي خطأ "قيمة '' ليست من بُنية تاريخ صحيحة"
        for field in self.fields.values():
            field.required = False

        if self.instance.pk:
            readonly_fields = ['status', 'dayDate', 'place_text', 'place_link', 'section_place_link']
            for field in readonly_fields:
                if field in self.fields:
                    self.fields[field].disabled = True
                    value = self.initial.get(field) or getattr(self.instance, field, None)
                    if isinstance(self.fields[field], forms.ModelChoiceField):
                        self.fields[f'{field}_hidden'] = forms.ModelChoiceField(
                            queryset=self.fields[field].queryset,
                            initial=value,
                            widget=forms.HiddenInput(),
                            required=False
                        )
                    elif isinstance(self.fields[field], forms.DateField):
                        self.fields[f'{field}_hidden'] = forms.DateField(
                            initial=value,
                            widget=forms.HiddenInput(),
                            required=False
                        )
                    else:
                        self.fields[f'{field}_hidden'] = forms.CharField(
                            initial=value,
                            widget=forms.HiddenInput(),
                            required=False
                        )



    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        dayDate = cleaned_data.get('dayDate')

        if employee and dayDate:
            qs = EmployeeAttendance.objects.filter(employee=employee, dayDate=dayDate)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Attendance for this employee on this date already exists.")

class EmployeeAttendanceInline(admin.TabularInline):
    model = EmployeeAttendance
    form = EmployeeAttendanceInlineForm
    extra = 0
    can_delete = False

    def get_extra(self, request, obj=None, **kwargs):
        # Show 1 empty row if no attendance exists, else 0
        return 1 if not obj or not obj.employeeattendance_set.exists() else 0

    def has_add_permission(self, request, obj=None):
        return True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        original_form_init = formset.form.__init__

        def custom_form_init(form_self, *args, **kwargs):
            original_form_init(form_self, *args, **kwargs)
            if not form_self.instance.pk:
                # Enable all fields for new blank row
                for field in form_self.fields.values():
                    field.disabled = False
                    field.widget.attrs.pop('disabled', None)

        formset.form.__init__ = custom_form_init
        return formset
    
class EmployeeAdmin(admin.ModelAdmin):
    list_filter = ()
    model = Employee
    form = EmployeeChangeForm
    change_form_template = 'admin/employee_change_form.html'
    inlines = [EmploymentHistoryInline, CourseInline, PenaltyInline, SecretReportInline,EmployeeVacationInline,EmployeeAttendanceInline]  # Keep inlines here
    readonly_fields = ('periodicVacations', 'casualVacations', 'birthGovernorate', 'birthDivision', 'academicQualifications')

    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:employee_id>/toggle-active/',
                self.admin_site.admin_view(self.toggle_active_view),
                name='employee-toggle-active',
            ),
        ]
        return custom_urls + urls

    def toggle_active_view(self, request, employee_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        
        employee = get_object_or_404(Employee, pk=employee_id)
        employee.is_active = not employee.is_active
        employee.save()
        
        if employee.is_active:
            messages.success(request, f'تم تفعيل الموظف {employee.firstName}.')
        else:
            messages.success(request, f'تم إلغاء تفعيل الموظف {employee.firstName}.')
        
        return redirect('admin:base_employee_change', employee_id)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_toggle_button'] = True
        return super().change_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        class WrappedForm(form_class):
            def __new__(cls, *args, **form_kwargs):
                form_kwargs['request'] = request
                return form_class(*args, **form_kwargs)

        return WrappedForm


    def number_of_penalties(self, obj):
        return obj.penalties.count()

    number_of_penalties.short_description = _('Penalties')
    list_display = ('firstName', 'secondName', 'number_of_penalties', 'is_active')

    fieldsets = (
        (_('البيانات الشخصية'), {
            'classes': ('tab', 'personal-info'),
            'fields': (
                ('employee_image',),
                ('firstName', 'secondName', 'thirdName', 'lastName'),
                ('nationalId', 'birthDate'),
                ('gender', 'religion'),
                ('birthGovernorateFF','birthGovernorate'),
                ('birthDivisionFF', 'birthDivision'),
                ('addressGovernorateFF', 'addressGovernorate'),
                ('addressDivisionFF','addressDivision'),
            )
        }),
        (_('البيانات الوظيفية'), {
            'classes': ('tab', 'employment-info'),
            'fields': (
                ('employmentDate', 'decisionNumber', 'jobStartDate', 'currentRank'),
                ('insuranceNumber', 'healthInsuranceNumber'),
                ('previousHaj', 'previousHajDate'),
                ('retirementDate'),
                ('jobFamily', 'graduationYear', 'militaryStatus'),
                ('solidarityFund', 'solidarityFundDate'),
                ('stakeholderFund', 'stakeholderFundDate'),
                ('insuranceUmbrella', 'insuranceUmbrellaDate'),
                ('academicQualificationsFF', 'academicQualifications'),
            ),
        }),
        (_('جهات العمل'), {
            'classes': ('tab', 'employer-info'),
            'fields': ('currentEmployer', 'currentEmployerSection', 'currentEmploymentStartDate'),
        }),
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
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        request = self.request
        # تحقق من الحقول المطلوبة
        missing_fields = []

        if not self.cleaned_data.get('birthGovernorateFF'):
            missing_fields.append(str(_('Birth Governorate')))
        if not self.cleaned_data.get('addressGovernorateFF'):
            missing_fields.append(str(_('Address Governorate')))
        if not self.cleaned_data.get('addressDivisionFF'):
            missing_fields.append(str(_('Address Division')))
        if not self.cleaned_data.get('birthDivisionFF'):
            missing_fields.append(str(_('Birth Division')))

        # if missing_fields and self.request:
        #     messages.warning(self.request, f"يرجى ملء الحقول التالية: {', '.join(missing_fields)}")
        #     raise ValidationError("الرجاء استكمال البيانات المطلوبة.")

        # حفظ البيانات الإضافية
        instance.birthGovernorate = self.cleaned_data.get('birthGovernorateFF')
        gov = self.cleaned_data.get('addressGovernorateFF')
        instance.addressGovernorate = gov if gov else instance.addressGovernorate
        instance.birthDivision = self.cleaned_data.get('birthDivisionFF').name if self.cleaned_data.get('birthDivisionFF') else instance.birthDivision
        instance.addressDivision = self.cleaned_data.get('addressDivisionFF').name if self.cleaned_data.get('addressDivisionFF') else instance.addressDivision
        instance.academicQualifications = self.cleaned_data.get('academicQualificationsFF').name if self.cleaned_data.get('academicQualificationsFF') else instance.academicQualifications

        # تحقق من الرقم القومي
        nationalId = self.cleaned_data.get('nationalId', '')
        birthDate = self.cleaned_data.get('birthDate')
        gender = self.cleaned_data.get('gender')
        governorate = instance.birthGovernorate.name if instance.birthGovernorate else None
        # print(f"nationalId:{nationalId}, birthDate:{birthDate}, gender:{gender}, governorate:{governorate}")
        validation_result = self._validate_national_id(nationalId, birthDate, gender, governorate)
        # print(f"validation_result: {validation_result}")
        
        if validation_result == 6:
            messages.error(request, 'المحافظة غير مطابقة للرقم القومي')
            return instance
        elif validation_result == 7:
            messages.error(request, 'المحافظة غير موجودة في قاعدة البيانات')
            return instance
        elif validation_result == 5:
            messages.error(request, 'النوع غير مطابق لرقم البطاقة')
            return instance
        elif validation_result != True:
            messages.error(request, 'الرقم القومي غير صحيح')
            return instance
        if commit and not self.errors:
            instance.save()

        return instance

    class Media:
        css = {'all': ('base/custom_admin.css',)}
        js = (
            'base/js/admin_tabs.js',
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'base/js/admin_custom.js',
            'base/js/disable_today.js',
            'base/js/employee_print.js',
            )

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