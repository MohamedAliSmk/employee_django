from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime

def validate_date(value):
    try:
        # datetime.strptime(value, '%Y-%m-%d')
        if value > timezone.now().date():
            raise ValidationError(_("The date cannot be in the future"))
    except ValueError:
        raise ValidationError(_('Invalid date - it must be in YYYY-MM-DD format.'))


# Create your models here.
class CustomUser(AbstractUser):
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
    birthPlace = models.TextField(_('Birth Place'), null=True, blank=True)
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
    
    academicQualifications = models.TextField(_('Academic Qualifications'), null=True, blank=True)
    jobFamily = models.CharField(_('Job Family'), max_length=200, null=True, blank=True)
    graduationYear = models.DateField(_('Graduation Year'), validators=[validate_date], null=True, blank=True)
    academicQualificationsInService = models.TextField(_('Academic Qualifications In Service'), null=True, blank=True)
    
    employmentDate = models.DateField(_('Employment Date'), validators=[validate_date], null=True, blank=True)
    decisionNumber = models.CharField(_('Decision Number'), max_length=200, null=True, blank=True)
    militaryStatus = models.CharField(_('Military Status'), max_length=200, null=True, blank=True)
    jobStartDate = models.DateField(_('Job Start Date'), validators=[validate_date], null=True, blank=True)
    currentRank = models.CharField(_('Current Rank'), max_length=200, null=True, blank=True)
    previousEmployer = models.CharField(_('Previous Employer'), max_length=200, null=True, blank=True)
    currentEmployer = models.CharField(_('Current Employer'), max_length=200, null=True, blank=True)
    idealEmployee = models.BooleanField(_('Ideal Employee'), default=False, null=True, blank=True)
    policeDayHonoring = models.BooleanField(_('Police Day Honoring'), default=False, null=True, blank=True)
    periodicVacations = models.IntegerField(_('Periodic Vacations'), validators=[MinValueValidator(0)], null=True, blank=True)
    casualVacations = models.IntegerField(_('Casual Vacations'), validators=[MinValueValidator(0)], null=True, blank=True)
    
    retirementDate = models.DateField(_('Retirement Date'), validators=[validate_date], null=True, blank=True)
    solidarityFund = models.TextField(_('Solidarity Fund'), null=True, blank=True)
    stakeholderFund = models.TextField(_('stakeholder Fund'), null=True, blank=True)
    insuranceUmbrella = models.TextField(_('Insurance Umbrella'), null=True, blank=True)
    
    address = models.TextField(_('Address'), null=True, blank=True)
    religion = models.CharField(_('Religion'), max_length=200, null=True, blank=True)
    notes = models.TextField(_('Notes'), null=True, blank=True)
    previousHaj = models.BooleanField(_('Previous Haj'), default=False, null=True, blank=True)
    
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
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    type = models.CharField(_('Type'), max_length=200, choices=TYPES, null=False, blank=False)
    name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
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
    name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    description = models.TextField(_('Description'), null=False, blank=False)
    reportDate = models.DateField(_('Report Date'), validators=[validate_date], null=True, blank=True)
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Secret Report')
        verbose_name_plural = _('Secret Reports')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    name = models.CharField(_('Name'), max_length=200, null=False, blank=False)
    description = models.TextField(_('Description'), null=True, blank=True)
    startDate = models.DateField(_('Start Date'), validators=[validate_date], null=True, blank=True)
    endDate = models.DateField(_('End Date'), validators=[validate_date], null=True, blank=True)
    certificateObtained = models.BooleanField(_('Obtained Certificate'), default=False, null=True, blank=True)
    grade = models.CharField(_('Grade'), max_length=200, null=True, blank=True)
    
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class IdealEmployeeCandidate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    idealEmployee = models.BooleanField(_('Ideal Employee'), default=False, null=True, blank=True)
    created = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ideal Employee Candidate')
        verbose_name_plural = _('Ideal Employee Candidates')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.user.username)
    
    def save(self, *args, **kwargs):
        user = CustomUser.objects.get(username=self.user)
        user.idealEmployee = self.idealEmployee
        user.save()

        super(IdealEmployeeCandidate, self).save(*args, **kwargs)
    
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
    