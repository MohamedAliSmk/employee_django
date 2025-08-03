import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.db import transaction
from smart_selects.db_fields import ChainedForeignKey
from .helpers import validate_date

class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser.
    Adds the 'is_staff' field explicitly.
    """
    is_staff = models.BooleanField(
        default=True,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text='حدد ما إذا كان هذا المستخدم نشط أم لا. قم بإلغاء التحديد بدلاً من حذف الحسابات.',
    )

class Penalty(models.Model):
    TYPES =( 
        ("disciplinary", "إنضباطية"), 
        ("behavioral", "مسلكية"), 
    )    
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name=_('User'), related_name='penalties')
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee'), related_name='penalties')
    
    type = models.CharField(_('Type'), max_length=200, choices=TYPES, null=False, blank=False)
    # name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    penaltyDate = models.DateField(_('Penalty Date'), validators=[validate_date], null=True, blank=True)
    description = models.TextField(_('Description'), null=False, blank=False,validators=[arabic_validator])
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Penalty')
        verbose_name_plural = _('Penalties')
        ordering = ['-updated', '-created']
    def __str__(self):
        return f"{self.get_type_display()} - {self.description[:50]}"
    
class SecretReport(models.Model):
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name=_('User'))
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee'))
    
    # name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    reportDateFrom = models.DateField(_('Report Date From'), validators=[validate_date], null=True, blank=True)
    reportDateTo = models.DateField(_('Report Date To'), validators=[validate_date], null=True, blank=True)
    description = models.TextField(_('Description'), null=False, blank=False,validators=[arabic_validator])
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Secret Report')
        verbose_name_plural = _('Secret Reports')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.description)
    
class Course(models.Model):
    GRADES =( 
        ("Failed", "رسوب"),
        ("Fair", "مقبول"),
        ("Good", "جيد"),
        ("Very Good", "جبد جدا"),
        ("Excellent", "امتياز"),
    )  
        
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee'))

    name = models.CharField(_('Course Name'), max_length=200, null=False, blank=False)
    address = models.CharField(_('Course Address'), max_length=200, null=True, blank=True)
    # startDate = models.DateField(_('Start Date'), validators=[validate_date], null=True, blank=True)
    # endDate = models.DateField(_('End Date'), validators=[validate_date], null=True, blank=True)
    grade = models.CharField(_('Grade'), max_length=200, choices=GRADES, null=True, blank=True)
    certificateObtained = models.BooleanField(_('Obtained Certificate'), default=False, null=True, blank=True)
    CertDate = models.DateField(_('تاريخ الحصول علي الشهادة'), null=True, blank=True) #make this hidden if certificateObtained is 0
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class IdealEmployee(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name=_('User'))
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee'))
    
    date = models.DateField(_('Date'), validators=[validate_date], null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ideal Employee')
        verbose_name_plural = _('Ideal Employees')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.employee.firstName)
    
    # def save(self, *args, **kwargs):
    #     user = CustomUser.objects.get(username=self.user)
    #     user.idealEmployee = self.idealEmployee
    #     user.save()

    #     super(IdealEmployeeCandidate, self).save(*args, **kwargs)
    
class PoliceDayHonoredEmployee(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name=_('User'))
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee'))
    
    date = models.DateField(_('Date'), validators=[validate_date], null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Police Day Honored Employee')
        verbose_name_plural = _('Police Day Honored Employee')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.employee.firstName)

class DepartmentsAndSections(models.Model):
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s/-]+$',
        message=_('الإدخال باللغة العربية فقط ويسمح بالمسافات والرموز "/" و "-"')
    )
    name = models.CharField(_('الإدارة / القسم'), max_length=255, validators=[arabic_validator], unique=True)
    DepartmentsAndSections_id = models.IntegerField(_('الرقم التسلسلي'), unique=True)  # Renamed for clarity

    class Meta:
        verbose_name = _('الإدارات والأقسام')
        verbose_name_plural = _('الإدارات والأقسام')

    def __str__(self):
        return f"{self.name}"

class Sections(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    department = models.ForeignKey(DepartmentsAndSections, related_name='sections', on_delete=models.CASCADE)  # Updated related_name

    class Meta:
        verbose_name = _('Sections')
        verbose_name_plural = _('Sections')

    def __str__(self):
        return f"{self.name}"

class EmployeeAttendance(models.Model):
    STATUSES = (
        ("P", "بالعمل"),  # present
        ("S", "مرضي"),  # sick
        ("C", "عارضة"),  # casual
        ("A", "دوري"),  # annual
        ("M", "غياب"),  # missing
        ("O", "راحة"),  # missing
        ("F", "دورة تدريبية"),  # missing
        ("IMS", "مأمورية داخلية"),  
        ("OMS", "مأمورية خارجية"),  
        ("P65%", "بالعمل خمسة وستون"),  # present
        ("l", "اجازة بدون مرتب"),  # leave without pay
    )

    employee = models.ForeignKey(
        'Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee')
    )
    status = models.CharField(_('Status'), max_length=200, choices=STATUSES, null=False, blank=False)
    dayDate = models.DateField(
        _('Day Date'), 
        default=datetime.now,
        null=False, blank=False
    )

    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    # New field for place selection
    place_text = models.CharField(_('مكان المأمورية الخارجية'), max_length=255,validators=[arabic_validator], blank=True, null=True)
    place_link = models.ForeignKey(DepartmentsAndSections, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("الإدارة"))
    section_place_link = ChainedForeignKey(
        Sections,
        chained_field="place_link",         # field in this model that is the parent
        chained_model_field="department",     # field in the Sections model that relates to DepartmentsAndSections
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )
    class Meta:
        verbose_name = _('Employee Attendance')
        verbose_name_plural = _('Employees Attendance')
        ordering = ['-updated', '-created']
        unique_together = ('employee', 'dayDate')  # Database-level constraint

    def clean(self):
        pass
        # # Model validation for duplicate records
        # if EmployeeAttendance.objects.filter(employee=self.employee, dayDate=self.dayDate).exists():
        #     raise ValidationError(_('Attendance record for this employee on this date already exists.'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee.firstName
    
class AcademicQualification(models.Model):
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    name = models.CharField(_('Qualification Name'), max_length=200, null=False, blank=False, unique=True,validators=[arabic_validator])
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Academic Qualification')
        verbose_name_plural = _('Academic Qualifications')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)

class Governorate(models.Model):
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    name = models.CharField(_('Name'), max_length=100, unique=True,validators=[arabic_validator])
    national_governorate_id = models.IntegerField(_('الرقم التسلسلي للمحافظة'), unique=True)
    class Meta:
        verbose_name = _('Governorate')
        verbose_name_plural = _('Governorates')
    def __str__(self):
        return (self.name)
    
class Division(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    governorate = models.ForeignKey(Governorate, related_name='divisions', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Division')
        verbose_name_plural = _('Divisions')
    def __str__(self):
        return (self.name)
    
class CourseName(models.Model):
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )

    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
        validators=[arabic_validator]
    )

    class Meta:
        verbose_name = _('Course Name')
        verbose_name_plural = _('Course Names')

    def __str__(self):
        return self.name

class EmployeeVacation(models.Model):
    TYPES =( 
        ("Periodic", "دورية"),
        ("Casual", "عارضة"),
        ("Sick", "مرضى"),
        ("Rest", "راحة"),
        ("Course", "دورة تدريبية"),
        # ("Inside Mission", "مأمورية داخلية"),
        # ("Outside Mission", "مأمورية خارجية"),
        # ("P65%", "بالعمل خمسة وستون"),
        ("Leave Without Pay", "اجازة بدون مرتب"),
    )   
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name=_('User'))
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, verbose_name=_('Employee'))

    type = models.CharField(_('Type'), max_length=200, choices=TYPES, null=False, blank=False)
    
    fromDate = models.DateField(_('From Date'), null=True, blank=True)
    toDate = models.DateField(_('To Date'), null=True, blank=True)
    days = models.IntegerField(_('Days'), editable=False, null=True, blank=True)
    remainingBalance = models.IntegerField(_('Remaining Balance'), editable=False, null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    # New field for place selection
    # place_text = models.CharField(_('مكان المأمورية الخارجية'), max_length=255,validators=[arabic_validator], blank=True, null=True)
    # place_link = models.ForeignKey(DepartmentsAndSections, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("الإدارة - القسم"))
    # section_place_link =  ChainedForeignKey(
    #     Sections,
    #     chained_field="place_link",         # field in this model that is the parent
    #     chained_model_field="department",     # field in the Sections model that relates to DepartmentsAndSections
    #     show_all=False,
    #     auto_choose=True,
    #     sort=True,
    #     null=True,
    #     blank=True,
    #     verbose_name=_("القسم")
    # )
    class Meta:
        verbose_name = _('Employee Vacation')
        verbose_name_plural = _('Employee Vacations')
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.employee.firstName if self.employee else "Vacation without Employee"


    def save(self, *args, **kwargs):
        # Skip validation if dates are empty
        if not self.fromDate or not self.toDate:
            super().save(*args, **kwargs)
            return

        # Calculate days
        delta = self.toDate - self.fromDate
        self.days = delta.days + 1  # Include both start and end dates

        # Validate vacation balance
        if self.type == 'Periodic':
            # Get current periodic vacation balance
            current_balance = self.employee.periodicVacations if self.employee else 0
            if self.days > current_balance:
                raise ValidationError('رصيد الإجازة الدورية غير كافي.')

        elif self.type == 'Casual':
            # Get current casual vacation balance
            current_balance = self.employee.casualVacations if self.employee else 0
            if self.days > current_balance:
                raise ValidationError('رصيد الإجازة العرضية غير كافي.')

        super().save(*args, **kwargs)

class Employee(models.Model):
    MILITARY_STATUSES =( 
        ("Completed", "تم الخدمة"),
        ("Permanently Exempted", "معافى نهائيًا"), 
        ("Temporarily Exempted", "معافى مؤقتًا"),
        ("Draft Evader", "متخلف عن التجنيد"),
        ("Deferred Conscription", "مؤجل التجنيد"), 
        ("Not Required for Conscription", "غير مطلوب للتجنيد"), 
    )  
    EMPLOYEE_RANKS =( 
        ("First Grade A", "الدرجة الأولى ا"),
        ("First Grade B", "الدرجة الأولى ب"),
        ("Second Grade A", "الدرجة الثانية ا"),
        ("Second Grade B", "الدرجة الثانية ب"),
        ("Third Grade A", "الدرجة الثالثة ا"),
        ("Third Grade B", "الدرجة الثالثة ب"),
        ("Fourth Grade A", "الدرجة الرابعة ا"),
        ("Fourth Grade B", "الدرجة الرابعة ب"),
    )  
    RELIGION =( 
        ("Muslim", "مسلم"),
        ("Christian", "مسيحى"),
    )  
    GENDER =( 
        ("Male", "ذكر"),
        ("Female", "أنثى"),
    )
    nationalId = models.CharField(
        _('National ID'),
        validators=[
            RegexValidator(
                regex=r'^([2-3]{1})([0-9]{2})(0[1-9]|1[012])(0[1-9]|[1-2][0-9]|3[0-1])(0[1-4]|[1-2][1-9]|3[1-5]|88)[0-9]{3}([0-9]{1})[0-9]{1}$',
                message=_("Enter a valid national id"),
                code=_("invalid_data"),
            ),
        ], 
        max_length=200, null=False, blank=False
    )
    # Image field with custom upload_to function
    def employee_image_path(instance, filename):
        return f"employees/{instance.nationalId}/{filename}"

    employee_image = models.ImageField(
        _('Employee Image'),
        upload_to=employee_image_path,
        null=True,
        blank=True
    )
    def image_preview(self):
        """
        Returns a modern, well-styled image preview for the admin panel.
        If no image is available, it displays a default placeholder.
        """
        if self.employee_image:
            return mark_safe(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 5px;
                ">
                    <img src="{self.employee_image.url}" 
                        style="border-radius: 10px; 
                                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                                border: 2px solid #ddd;
                                max-width: 120px;
                                max-height: 120px;
                                object-fit: cover;" />
                </div>
            """)
        return mark_safe("""
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                width: 120px;
                height: 120px;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 14px;
                border: 2px dashed #ddd;
                text-align: center;
                line-height: 120px;
            ">
                (No Image)
            </div>
        """)

    image_preview.short_description = _('Image Preview')
    arabic_validator = RegexValidator(
        regex=r'^[\u0600-\u06FF\s]+$',
        message=_('الإدخال باللغة العربية فقط')
    )
    firstName = models.CharField(_('First Name'), max_length=200, null=True, blank=True,validators=[arabic_validator])
    secondName = models.CharField(_('Second Name'), max_length=200, null=True, blank=True,validators=[arabic_validator])
    thirdName = models.CharField(_('Third Name'), max_length=200, null=True, blank=True,validators=[arabic_validator])
    lastName = models.CharField(_('Last Name'), max_length=200, null=True, blank=True,validators=[arabic_validator])
    birthGovernorate = models.ForeignKey(
            'Governorate',  # Model name of the related table (can be a string)
            verbose_name=_('Birth Governorate'),
            null=True, 
            blank=True, 
            on_delete=models.SET_NULL,  # You can change this to CASCADE if needed
        )
    birthDivision = models.CharField(_('Birth Division'), max_length=200, null=True, blank=True)    
    birthDate = models.DateField(
        _('Birth Date'), 
        default= datetime.now,
        validators=[validate_date],
        null=False, blank=False
    )

    full_name = models.CharField(max_length=255, null=True, blank=True,validators=[arabic_validator])
    gender = models.CharField(_('Gender'), max_length=200, choices=GENDER, null=False, blank=False, default="Male")
    
    insuranceNumber = models.CharField(_('Insurance Number'), max_length=200, null=True, blank=True)
    healthInsuranceNumber = models.CharField(_('Health Insurance Number'), max_length=200, null=True, blank=True)
    
    academicQualifications = models.CharField(_('Academic Qualifications'), max_length=200, null=True, blank=True)
    jobFamily = models.CharField(_('Job Family'), max_length=200, null=True, blank=True)
    graduationYear = models.DateField(_('Graduation Year'), validators=[validate_date], null=True, blank=True)
    
    employmentDate = models.DateField(_('Employment Date'), validators=[validate_date], null=True, blank=True)
    decisionNumber = models.CharField(_('Decision Number'), max_length=200, null=True, blank=True)
    militaryStatus = models.CharField(_('Military Status'), max_length=200, choices=MILITARY_STATUSES, null=True, blank=True)
    jobStartDate = models.DateField(_('Job Start Date'), validators=[validate_date], null=True, blank=True)
    currentRank = models.CharField(_('Current Rank'), max_length=200, choices=EMPLOYEE_RANKS, null=True, blank=True)
    
    # previousEmployer = models.CharField(_('Previous Employer'), max_length=200, null=True, blank=True)
    # previousEmploymentStartDate = models.DateField(_('Previous Employment Start Date'), null=True, blank=True)
    # previousEmploymentEndDate = models.DateField(_('Previous Employment End Date'), null=True, blank=True)
    
    currentEmployer =models.ForeignKey(DepartmentsAndSections, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("جهة العمل الحالية"))
    # currentEmployerSection =models.ForeignKey(Sections, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("القسم"))
    currentEmployerSection =  ChainedForeignKey(
        Sections,
        chained_field="currentEmployer",         # field in this model that is the parent
        chained_model_field="department",     # field in the Sections model that relates to DepartmentsAndSections
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True,
        verbose_name=_("القسم")
    )
    currentEmploymentStartDate = models.DateField(_('Current Employment Start Date'), null=True, blank=True)

    periodicVacations = models.IntegerField(_('Periodic Vacations'), validators=[MinValueValidator(0)], default=21, null=True, blank=True)
    casualVacations = models.IntegerField(_('Casual Vacations'), validators=[MinValueValidator(0)], default=7, null=True, blank=True)
    
    retirementDate = models.DateField(_('Retirement Date'), validators=[validate_date], null=True, blank=True)
    
    solidarityFund = models.BooleanField(_('Solidarity Fund'), default=False, null=False, blank=False)
    solidarityFundDate = models.DateField(_('Joining Date'), null=True, blank=True)
    stakeholderFund = models.BooleanField(_('stakeholder Fund'), default=False, null=False, blank=False)
    stakeholderFundDate = models.DateField(_('Joining Date'), null=True, blank=True)
    insuranceUmbrella = models.BooleanField(_('Insurance Umbrella'), default=False, null=False, blank=False)
    insuranceUmbrellaDate = models.DateField(_('Joining Date'), null=True, blank=True)
    
    addressGovernorate = models.CharField(_('Address Governorate'), max_length=200, null=True, blank=True)
    addressDivision = models.CharField(_('Address Division'), max_length=200, null=True, blank=True)
    
    religion = models.CharField(_('Religion'), max_length=200, choices=RELIGION, null=False, blank=False, default='Muslim')
    previousHaj = models.BooleanField(_('Previous Haj'), default=False, null=False, blank=False)
    previousHajDate = models.DateField(_('Previous Haj Date'), null=True, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text='حدد ما إذا كان هذا الموظف نشط أم لا. قم بإلغاء التحديد بدلاً من حذف الحسابات.',
    )
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    def __str__(self):
        return self.firstName

    def save(self, *args, **kwargs):
        try:
            if self.periodicVacations is None and self.currentEmploymentStartDate:
                yearsDateDifference = relativedelta(now().date(), self.currentEmploymentStartDate).years + 1
                self.periodicVacations = 30 if yearsDateDifference >= 30 else 21

            if self.periodicVacations is None and self.birthDate:
                birthYearsDateDifference = relativedelta(now().date(), self.birthDate).years + 1
                self.periodicVacations = 45 if birthYearsDateDifference >= 50 else self.periodicVacations

            
            if self.pk:  # Ensure it's an update
                # **Check if the same employment record already exists for the old employer**
                existing_history = EmploymentHistory.objects.filter(
                    employee=self,
                    employer_name=self.currentEmployer,
                    employer_section_name=self.currentEmployerSection,
                    start_date=self.currentEmploymentStartDate
                ).exists()
                if not existing_history:
                    with transaction.atomic():
                        EmploymentHistory.objects.create(
                            employee=self,
                            employer_name=self.currentEmployer,  # Save the old employer
                            employer_section_name=self.currentEmployerSection,
                            start_date=self.currentEmploymentStartDate
                        )

        except Exception as e:
            print(f"Error saving employee: {e}")
        try:
            old_instance = type(self).objects.get(pk=self.pk)
            if old_instance.employee_image and old_instance.employee_image.name:
                if old_instance.employee_image.name != self.employee_image.name:
                    old_image_path = old_instance.employee_image.path
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)
        except type(self).DoesNotExist:
            pass  # New object, no image to delete

        if self.periodicVacations is None:
            self.periodicVacations = 21

        if self.casualVacations is None:
            self.casualVacations = 7

        super(Employee, self).save(*args, **kwargs)  # Ensure final save
    
    def delete(self, *args, **kwargs):
        if self.employee_image and self.employee_image.name:
            image_path = self.employee_image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)

class EmploymentHistory(models.Model):
    """ Table to store previous employers """
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="employment_history"
    )
    employer_name = models.ForeignKey(
        DepartmentsAndSections, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        verbose_name=_("جهة العمل السابقة")
    )
    employer_section_name = models.ForeignKey(
        Sections, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        verbose_name=_("القسم")
    )
    start_date = models.DateField(_('تاريخ بداية العمل'))
    # end_date = models.DateField(_('تاريخ نهاية العمل'), null=True, blank=True)
    class Meta:
        verbose_name = _('جهات العمل السابقة')
        verbose_name_plural = _('جهات العمل السابقة')
    
    # def save(self, *args, **kwargs):
    #     if self.start_date and self.end_date and self.end_date < self.start_date:
    #         raise ValidationError(_('لا يمكن أن يكون تاريخ النهاية قبل تاريخ البداية.'))
    #     super(EmploymentHistory, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.firstName} - {self.employer_name} ({self.start_date}"