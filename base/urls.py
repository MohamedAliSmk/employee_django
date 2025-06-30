from django.urls import path,include
from . import views
from django.views.i18n import set_language
app_name = "base"
urlpatterns = [
    path('i18n/', set_language, name = 'set_language'),
    path('', views.home, name = 'home'),
    path('task', views.task, name = 'task'),
    path('divisions/<int:gov_id>/', views.get_divisions, name='get_divisions'),
    path('sections/<int:gov_id>/', views.get_sections, name='get_sections'),
    path('chaining/', include('smart_selects.urls')),
    path("employee/<int:employee_id>/print/<str:section>/", views.employee_section_print, name="employee_print_section"),

]
