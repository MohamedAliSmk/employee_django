from django.shortcuts import render
from django.http import HttpResponse
from .tasks import add_attendance_records

# Create your views here.
def home(request):
    return render(request, 'base/home.html')


def task(request):
    add_attendance_records()
    return HttpResponse('Done')