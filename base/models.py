from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class CustomUser(AbstractUser):
    secondName = models.CharField(_('Second Name'), max_length=200, null=True, blank=True)
    thirdName = models.CharField(_('Third Name'), max_length=200, null=True, blank=True)
    nickname = models.CharField(_('Nickname'), max_length=200, null=True, blank=True)
    birthPlace = models.TextField(_('Birth Place'), null=True, blank=True)
    birthDate = models.DateField(_('Birth Date'), null=True, blank=True)
    nationalId = models.CharField(_('National ID'), max_length=200, null=True, blank=True)
    
    insuranceNumber = models.CharField(_('Insurance Number'), max_length=200, null=True, blank=True)
    healthInsuranceNumber = models.CharField(_('Health Insurance Number'), max_length=200, null=True, blank=True)
    
    academicQualifications = models.TextField(_('Academic Qualifications'), null=True, blank=True)
    jobFamily = models.CharField(_('Job Family'), max_length=200, null=True, blank=True)
    graduationYear = models.DateField(_('Graduation Year'), null=True, blank=True)
    academicQualificationsInService = models.TextField(_('Academic Qualifications In Service'), null=True, blank=True)
    
    employmentDate = models.DateField(_('Employment Date'), null=True, blank=True)
    decisionNumber = models.CharField(_('Decision Number'), max_length=200, null=True, blank=True)
    militaryStatus = models.CharField(_('Military Status'), max_length=200, null=True, blank=True)
    jobStartDate = models.DateField(_('Job Start Date'), null=True, blank=True)
    currentRank = models.CharField(_('Current Rank'), max_length=200, null=True, blank=True)
    previousEmployer = models.CharField(_('Previous Employer'), max_length=200, null=True, blank=True)
    currentEmployer = models.CharField(_('Current Employer'), max_length=200, null=True, blank=True)
    topEmployee = models.CharField(_('Top Employee'), max_length=200, null=True, blank=True)
    policeDayHonoring = models.CharField(_('Police Day Honoring'), max_length=200, null=True, blank=True)
    periodicVacations = models.IntegerField(_('Periodic Vacations'), null=True, blank=True)
    casualVacations = models.IntegerField(_('Casual Vacations'), null=True, blank=True)
    
    retirementDate = models.DateField(_('Retirement Date'), null=True, blank=True)
    solidarityFund = models.TextField(_('Solidarity Fund'), null=True, blank=True)
    stakeholderFund = models.TextField(_('stakeholder Fund'), null=True, blank=True)
    insuranceUmbrella = models.TextField(_('Insurance Umbrella'), null=True, blank=True)
    
    address = models.TextField(_('Address'), null=True, blank=True)
    religion = models.CharField(_('Religion'), max_length=200, null=True, blank=True)
    notes = models.TextField(_('Notes'), null=True, blank=True)
    previousHaj = models.CharField(_('Previous Haj'), max_length=200, null=True, blank=True)
    
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
    type = models.CharField(_('Type'), max_length=200, choices=TYPES)
    name = models.CharField(_('Name'), max_length=200, null=True, blank=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Penalty')
        verbose_name_plural = _('Penalties')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class SecretReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    name = models.CharField(_('Name'), max_length=200, null=True, blank=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    reportDate = models.DateField(_('Report Date'), null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Secret Report')
        verbose_name_plural = _('Secret Reports')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    
class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('User'))
    name = models.CharField(_('Name'), max_length=200, null=True, blank=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    startDate = models.DateField(_('Start Date'), null=True, blank=True)
    endDate = models.DateField(_('End Date'), null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-updated', '-created']
    def __str__(self):
        return (self.name)
    