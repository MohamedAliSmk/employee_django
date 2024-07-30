from django.urls import path
from . import views
from django.views.i18n import set_language

urlpatterns = [
    path('i18n/', set_language, name = 'set_language'),
    path('', views.home, name = 'home'),
    path('task', views.task, name = 'task'),
    path('divisions/<int:gov_id>/', views.get_divisions, name='get_divisions'),
]
