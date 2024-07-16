# your_app/tasks.py
from datetime import timedelta
from django.utils import timezone
from .models import CustomUser, EmployeeAttendance

def add_attendance_records():
    today = timezone.now().date()
    start_date = today + timedelta(days=(4 - today.weekday()) % 7)  # Calculate next Friday
    end_date = start_date + timedelta(days=6)  # Next Thursday
    
    print('Starting ##########################')
    employees = CustomUser.objects.all()
    print('employees', employees)

    for employee in employees:
        for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
            print('single_date', single_date)
            status = 'P'
            if single_date.weekday() in (4, 5):
                status = 'O'
                
            EmployeeAttendance.objects.create(user=employee, status=status, dayDate=single_date)

# def add_attendance_records():
#     time = timezone.now().strftime('%X')
#     print("It's now %s" % time)