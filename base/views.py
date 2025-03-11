from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .tasks import add_attendance_records
from .models import Division, Sections
# from .helpers.national_id import validateNationalId

# Create your views here.
def home(request):
    return render(request, 'base/home.html')


def task(request):
    add_attendance_records()
    return HttpResponse('Done')

def get_divisions(request, gov_id):
    print('get_divisionsXXXXXXXXXXXXXXX')
    divisions = Division.objects.filter(governorate=gov_id).values('id', 'name')
    return JsonResponse(list(divisions), safe=False)

def get_sections(request):
    employer_id = request.GET.get('employer_id')
    
    print(f"Fetching sections for employer: {employer_id}")  # Debugging

    if employer_id:
        sections = Sections.objects.filter(governorate_id=employer_id).values("id", "name")
        return JsonResponse({"sections": list(sections)})

    return JsonResponse({"sections": []})