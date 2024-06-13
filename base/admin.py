from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Penalty, SecretReport, Course
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group

# Register your models here.
class CourseInline(admin.TabularInline):
    model = Course
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

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = CustomUserChangeForm
    inlines = [CourseInline, PenaltyInline, SecretReportInline]
    
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('nickname', 'birthPlace', 'birthDate')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('nickname', 'birthPlace', 'birthDate')}),
    # )
    fieldsets = (
        # (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'secondName', 'thirdName', 'last_name', 'nationalId', 'nickname', 'birthPlace', 'birthDate', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        # Add your additional custom fieldsets or modify existing ones as needed
        (_('Insurance info'), {'fields': ('insuranceNumber', 'healthInsuranceNumber')}),
        (_('Qualifications'), {'fields': ('academicQualifications', 'jobFamily', 'graduationYear', 'academicQualificationsInService')}),
        (
            _('Employment info'), {
                'fields': (
                    'employmentDate', 'decisionNumber', 'militaryStatus', 'jobStartDate', 'currentRank', 'previousEmployer', 'currentEmployer', 'topEmployee', 
                    'policeDayHonoring', 'retirementDate', 'periodicVacations', 'casualVacations'
                )
            }
        ),
        (
            _('Financial info'), {
                'fields': (
                    'solidarityFund', 'stakeholderFund', 'insuranceUmbrella'
                )
            }
        ),
        (_('Other info'), {'fields': ('address', 'religion', 'notes', 'previousHaj')}),
    )
    

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj or request.user.is_superuser:
            return fieldsets

        # Exclude specific fields for non-superusers
        exclude_fields = ('groups', 'user_permissions')
        return [
            (fieldset[0], {'fields': tuple(field for field in fieldset[1]['fields'] if field not in exclude_fields)})
            for fieldset in fieldsets
        ]


    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            print('is_superuser', request.user.is_superuser)
            return ()  # Return an empty tuple for superusers to have no read-only fields
        if not obj:  # When creating a new user, no fields are read-only
            return self.readonly_fields
        if request.user == obj:
            return [field.name for field in self.model._meta.fields if field.name not in ['first_name', 'username', 'nickname']]
        return self.readonly_fields

    # def has_add_permission(self, request):
    #     print('is_superuser', request.user.is_superuser)
    #     if request.user.is_superuser:
    #         return True
    #     return super().has_add_permission(request)

    # def has_change_permission(self, request, obj=None):
    #     print('Super:', request.user.is_superuser)
    #     if obj is not None and request.user.is_superuser:
    #         return True  # Superuser can edit all users
    #     if obj is not None and request.user == obj:
    #         return True  # User can edit their own record
    #     return False  # User cannot edit other users' records

    def has_view_permission(self, request, obj=None):
        if obj is not None and request.user == obj:
            return True
        return super().has_view_permission(request, obj)

    # def get_fields(self, request, obj=None):
    #     fields = super().get_fields(request, obj)
    #     if not request.user.is_superuser:
    #         # Exclude groups and user_permissions fields for normal users
    #         fields = [field for field in fields if field not in ['groups', 'user_permissions']]
    #     return fields

    # def get_exclude(self, request, obj=None):
    #     exclude = super().get_exclude(request, obj)
    #     if not request.user.is_superuser:
    #         # Exclude groups and user_permissions fields for normal users
    #         exclude = ['groups', 'user_permissions']
    #     return exclude

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset  # Superuser can see all users
        return queryset.filter(pk=request.user.pk)  # Normal user can only see their own record

# admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register([Penalty, SecretReport, Course])
admin.site.unregister(Group)