from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

def validate_date(value):
    try:
        # datetime.strptime(value, '%Y-%m-%d')
        if value > timezone.now().date():
            raise ValidationError(_("The date cannot be in the future"))
    except ValueError:
        raise ValidationError(_('Invalid date - it must be in YYYY-MM-DD format.'))


# Create your models here.
class CustomUser(AbstractUser):
    MILITARY_STATUSES =( 
        ("Completed", "تم الخدمة"),
        ("Permanently Exempted", "معافى نهائيًا"), 
        ("Temporarily Exempted", "معافى مؤقتًا"),
        ("Draft Evader", "متخلف عن التجنيد"),
        ("Deferred Conscription", "مؤجل التجنيد"), 
        ("Not Required for Conscription", "غير مطلوب للتجنيد"), 
    )  
    EMPLOYEE_RANKS =( 
        ("Rank 1", "درجة 1"),
        ("Rank 2", "درجة 2"),
        ("Rank 3", "درجة 3"),
    )  
    RELIGION =( 
        ("Muslim", "مسلم"),
        ("Christian", "مسيحى"),
    )  
    # username = models.CharField(
    #     _('Username'), 
    #     validators=[
    #         MinLengthValidator(8),
    #         RegexValidator(
    #             regex=r'^[0-9a-z]$',
    #             message=_("Enter a valid username - no spaces - all lowercase"),
    #             code=_("invalid_data"),
    #         ),
    #     ], 
    #     max_length=200, null=False, blank=False
    # )
    secondName = models.CharField(_('Second Name'), max_length=200, null=True, blank=True)
    thirdName = models.CharField(_('Third Name'), max_length=200, null=True, blank=True)
    nickname = models.CharField(_('Nickname'), max_length=200, null=True, blank=True)
    # birthPlace = models.TextField(_('Birth Place'), null=True, blank=True)
    
    birthGovernorate = models.CharField(_('Birth Governorate'), max_length=200, null=True, blank=True)
    birthDivision = models.CharField(_('Birth Division'), max_length=200, null=True, blank=True)
    
    birthDate = models.DateField(
        _('Birth Date'), 
        default= datetime.now,
        validators=[validate_date],
        null=False, blank=False
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
    
    insuranceNumber = models.CharField(_('Insurance Number'), max_length=200, null=True, blank=True)
    healthInsuranceNumber = models.CharField(_('Health Insurance Number'), max_length=200, null=True, blank=True)
    
    academicQualifications = models.CharField(_('Academic Qualifications'), max_length=200, null=True, blank=True)
    jobFamily = models.CharField(_('Job Family'), max_length=200, null=True, blank=True)
    graduationYear = models.DateField(_('Graduation Year'), validators=[validate_date], null=True, blank=True)
    # academicQualificationsInService = models.TextField(_('Academic Qualifications In Service'), null=True, blank=True)
    
    employmentDate = models.DateField(_('Employment Date'), validators=[validate_date], null=True, blank=True)
    decisionNumber = models.CharField(_('Decision Number'), max_length=200, null=True, blank=True)
    militaryStatus = models.CharField(_('Military Status'), max_length=200, choices=MILITARY_STATUSES, null=True, blank=True)
    jobStartDate = models.DateField(_('Job Start Date'), validators=[validate_date], null=True, blank=True)
    currentRank = models.CharField(_('Current Rank'), max_length=200, choices=EMPLOYEE_RANKS, null=True, blank=True)
    
    previousEmployer = models.CharField(_('Previous Employer'), max_length=200, null=True, blank=True)
    previousEmploymentStartDate = models.DateField(_('Previous Employment Start Date'), null=True, blank=True)
    previousEmploymentEndDate = models.DateField(_('Previous Employment End Date'), null=True, blank=True)
    
    currentEmployer = models.CharField(_('Current Employer'), max_length=200, null=True, blank=True)
    currentEmploymentStartDate = models.DateField(_('Current Employment Start Date'), null=True, blank=True)
    
    # idealEmployee = models.BooleanField(_('Ideal Employee'), default=False, null=True, blank=True)
    # policeDayHonoring = models.BooleanField(_('Police Day Honoring'), default=False, null=True, blank=True)
    periodicVacations = models.IntegerField(_('Periodic Vacations'), validators=[MinValueValidator(0)], default=15, null=True, blank=True)
    casualVacations = models.IntegerField(_('Casual Vacations'), validators=[MinValueValidator(0)], default=6, null=True, blank=True)
    
    retirementDate = models.DateField(_('Retirement Date'), validators=[validate_date], null=True, blank=True)
    
    solidarityFund = models.BooleanField(_('Solidarity Fund'), default=False, null=True, blank=True)
    solidarityFundDate = models.DateField(_('Joining Date'), null=True, blank=True)
    stakeholderFund = models.BooleanField(_('stakeholder Fund'), default=False, null=True, blank=True)
    stakeholderFundDate = models.DateField(_('Joining Date'), null=True, blank=True)
    insuranceUmbrella = models.BooleanField(_('Insurance Umbrella'), default=False, null=True, blank=True)
    insuranceUmbrellaDate = models.DateField(_('Joining Date'), null=True, blank=True)
    
    # address = models.TextField(_('Address'), null=True, blank=True)
    
    addressGovernorate = models.CharField(_('Address Governorate'), max_length=200, null=True, blank=True)
    addressDivision = models.CharField(_('Address Division'), max_length=200, null=True, blank=True)
    
    religion = models.CharField(_('Religion'), max_length=200, choices=RELIGION, null=True, blank=True)
    # notes = models.TextField(_('Notes'), null=True, blank=True)
    previousHaj = models.BooleanField(_('Previous Haj'), default=False, null=True, blank=True)
    previousHajDate = models.DateField(_('Previous Haj Date'), null=True, blank=True)
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Add related_name to avoid clashes
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Add related_name to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )

    def __str__(self):
        return self.username
    
class Penalty(models.Model):
    TYPES =( 
        ("disciplinary", "إنضباطية"), 
        ("behavioral", "مسلكية"), 
    )    
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'), related_name='penalties')
    type = models.CharField(_('Type'), max_length=200, choices=TYPES, null=False, blank=False)
    name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    penaltyDate = models.DateField(_('Penalty Date'), validators=[validate_date], null=True, blank=True)
    description = models.TextField(_('Description'), null=False, blank=False)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Penalty')
        verbose_name_plural = _('Penalties')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class SecretReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    # name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    reportDateFrom = models.DateField(_('Report Date From'), validators=[validate_date], null=True, blank=True)
    reportDateTo = models.DateField(_('Report Date To'), validators=[validate_date], null=True, blank=True)
    description = models.TextField(_('Description'), null=False, blank=False)
    
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
        
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    name = models.CharField(_('Course Name'), max_length=200, null=False, blank=False)
    address = models.CharField(_('Course Address'), max_length=200, null=True, blank=True)
    startDate = models.DateField(_('Start Date'), validators=[validate_date], null=True, blank=True)
    endDate = models.DateField(_('End Date'), validators=[validate_date], null=True, blank=True)
    certificateObtained = models.BooleanField(_('Obtained Certificate'), default=False, null=True, blank=True)
    grade = models.CharField(_('Grade'), max_length=200, choices=GRADES, null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class IdealEmployee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    date = models.DateField(_('Date'), validators=[validate_date], null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ideal Employee')
        verbose_name_plural = _('Ideal Employees')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.user.username)
    
    # def save(self, *args, **kwargs):
    #     user = CustomUser.objects.get(username=self.user)
    #     user.idealEmployee = self.idealEmployee
    #     user.save()

    #     super(IdealEmployeeCandidate, self).save(*args, **kwargs)
    
class PoliceDayHonoredEmployee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    date = models.DateField(_('Date'), validators=[validate_date], null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Police Day Honored Employee')
        verbose_name_plural = _('Police Day Honored Employee')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.user.username)

class EmployeeAttendance(models.Model):
    STATUSES =( 
        ("P", "ح"), # present 
        ("S", "م"), # sick
        ("C", "ع"), # casual
        ("A", "د"), # annual
        ("M", "غ"), # missing
        ("O", "ر"), # missing
    )   
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    status = models.CharField(_('Status'), max_length=200, choices=STATUSES, null=False, blank=False)
    dayDate = models.DateField(
        _('Day Date'), 
        default= datetime.now,
        validators=[validate_date],
        null=False, blank=False
    )
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Employee Attendance')
        verbose_name_plural = _('Employees Attendance')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.user.username)
    
    # def save(self, *args, **kwargs):
    #     user = CustomUser.objects.get(username=self.user)
    #     user.idealEmployee = self.idealEmployee
    #     user.save()
    #     super(IdealEmployeeCandidate, self).save(*args, **kwargs)
    
class AcademicQualification(models.Model):
    name = models.CharField(_('Qualification Name'), max_length=200, null=False, blank=False)
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Academic Qualification')
        verbose_name_plural = _('Academic Qualifications')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)

class Governorate(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    
    class Meta:
        verbose_name = _('Governorate')
        verbose_name_plural = _('Governorates')
    def __str__(self):
        return (self.name)
    
class Division(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    governorate = models.ForeignKey(Governorate, related_name='divisions', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Division')
        verbose_name_plural = _('Divisions')
    def __str__(self):
        return (self.name)
    
class EmployeeVacation(models.Model):
    TYPES =( 
        ("Periodic", "دورية"),
        ("Casual", "عارضة"),
        ("Sick", "مرضى"),
    )   
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    type = models.CharField(_('Type'), max_length=200, choices=TYPES, null=False, blank=False)
    
    fromDate = models.DateField(_('From Date'), null=True, blank=True)
    toDate = models.DateField(_('To Date'), null=True, blank=True)
    days = models.IntegerField(_('Days'), editable=False, null=True, blank=True)
    remainingBalance = models.IntegerField(_('Remaining Balance'), editable=False, null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Employee Vacation')
        verbose_name_plural = _('Employee Vacations')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.user.username)
    
    def save(self, *args, **kwargs):
        daysDiff = self.toDate - self.fromDate
        days = daysDiff.days + 1
        self.days = days
        
        user = CustomUser.objects.get(username=self.user)
        status = 'P'
        if self.type == 'Periodic':
            status = 'A'
            user.periodicVacations -= days
            self.remainingBalance = user.periodicVacations
            user.save()
            
        if self.type == 'Casual':
            status = 'C'
            user.casualVacations -= days
            self.remainingBalance = user.casualVacations
            user.save()
        
        if self.type == 'Sick':
            status = 'S'
            
        # date_list = []
        # current_date = self.fromDate
        # while current_date <= self.toDate:
        #     date_list.append(current_date)
        #     current_date += timedelta(days=1)
            
        # for date in date_list:
        #     print(date.strftime('%Y-%m-%d'))
            
        attendance = EmployeeAttendance.objects.filter(dayDate__range=(self.fromDate, self.toDate), user=self.user)
        attendance.update(status=status)
        
        super(EmployeeVacation, self).save(*args, **kwargs)
