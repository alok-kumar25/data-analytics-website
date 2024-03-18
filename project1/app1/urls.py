from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('logout/',views.logout_user,name='logout'),
    path('register/', views.register_user, name='register'),
    path('upload_csv/',views.upload_csv,name='upload'),
    path('reports/',views.reports,name="report"),
    path('reports/<str:file_name>/<int:t>/', views.reports, name='report_with_file')
]