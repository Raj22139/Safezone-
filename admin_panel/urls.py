from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('',                        views.admin_dashboard,    name='dashboard'),
    path('analytics/',              views.analytics,          name='analytics'),
    path('crimes/',                 views.crime_list,         name='crime_list'),
    path('crimes/add/',             views.crime_add,          name='crime_add'),
    path('crimes/<int:pk>/edit/',   views.crime_edit,         name='crime_edit'),
    path('crimes/<int:pk>/delete/', views.crime_delete,       name='crime_delete'),
    path('crimes/import/',          views.crime_import_redirect, name='crime_import'),
    path('areas/',                  views.area_list,          name='area_list'),
    path('areas/add/',              views.area_add,           name='area_add'),
    path('areas/<int:pk>/edit/',    views.area_edit,          name='area_edit'),
    path('areas/<int:pk>/delete/',  views.area_delete,        name='area_delete'),
    path('users/',                  views.user_list,          name='user_list'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle'),
    path('pending/',                views.pending_reports,    name='pending'),
    path('pending/<int:pk>/approve/', views.approve_report,  name='approve'),
    path('pending/<int:pk>/reject/',  views.reject_report,   name='reject'),
    path('user-reports/',           views.user_reports_list,  name='user_reports'),
]
