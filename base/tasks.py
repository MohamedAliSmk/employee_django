# your_app/tasks.py
from datetime import timedelta
from django.utils import timezone

def add_attendance_records():
    from .models import EmployeeAttendance, Employee  # Import necessary models
    
    today = timezone.now().date()
    
    employees = Employee.objects.all()
    
    for employee in employees:
        status = 'P'  # Default status
        
        # Check if attendance record for today already exists to avoid duplication
        attendance, created = EmployeeAttendance.objects.get_or_create(
            employee=employee, 
            dayDate=today,
            defaults={'status': status}
        )
        
