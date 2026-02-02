from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # CSV upload
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    
    # Data endpoints
    path('summary/<int:session_id>/', views.get_summary, name='get_summary'),
    path('equipment/<int:session_id>/', views.get_equipment_list, name='get_equipment_list'),
    path('history/', views.get_history, name='get_history'),
    path('charts/<int:session_id>/', views.get_chart_data, name='get_chart_data'),
    
    # PDF generation
    path('pdf/<int:session_id>/', views.generate_pdf, name='generate_pdf'),
]
