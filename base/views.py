from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .tasks import add_attendance_records
from .models import Division, Sections, Employee
# Create your views here.
def home(request):
    return render(request, 'base/home.html')


def task(request):
    add_attendance_records()
    return HttpResponse('Done')

def get_divisions(request, gov_id):
    divisions = Division.objects.filter(governorate=gov_id).values('id', 'name')
    return JsonResponse(list(divisions), safe=False)

def get_sections(request):
    employer_id = request.GET.get('employer_id')
    
    print(f"Fetching sections for employer: {employer_id}")  # Debugging

    if employer_id:
        sections = Sections.objects.filter(governorate_id=employer_id).values("id", "name")
        return JsonResponse({"sections": list(sections)})

    return JsonResponse({"sections": []})

from django.utils.dateparse import parse_date

def employee_section_print(request, employee_id, section):
    employee = get_object_or_404(Employee, pk=employee_id)
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    template_map = {
        "personal": "print_sections/personal_info.html",
        "employment": "print_sections/employment_info.html",
        "employer": "print_sections/employer_info.html",
        "course_set": "print_sections/course_set-group.html",
        "employeevacation_set": "print_sections/employeevacation_set-group.html",
        "penalties": "print_sections/penalties-group.html",
        "secretreport_set": "print_sections/secretreport_set-group.html",
        "employeeattendance_set": "print_sections/employeeattendance_set-group.html",
    }

    template_name = template_map.get(section)
    if not template_name:
        return render(request, "404.html")

    context = {"employee": employee}

    # تطبيق الفلترة على الحقول التي تدعمها
    if section == "employeevacation_set":
        queryset = employee.employeevacation_set.all()
        if from_date:
            queryset = queryset.filter(fromDate__gte=parse_date(from_date))
        if to_date:
            queryset = queryset.filter(toDate__lte=parse_date(to_date))
        context["vacations"] = queryset

    elif section == "employeeattendance_set":
        queryset = employee.employeeattendance_set.all()
        if from_date:
            queryset = queryset.filter(dayDate__gte=parse_date(from_date))
        if to_date:
            queryset = queryset.filter(dayDate__lte=parse_date(to_date))
        context["attendances"] = queryset

    return render(request, template_name, context)
