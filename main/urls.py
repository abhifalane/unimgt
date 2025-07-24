from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('student/register/', views.student_register, name='student_register'),
    path('custom_admin/login/', views.admin_login, name='admin_login'),
    path('custom_admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom_admin/add_marks/<int:student_id>/', views.add_marks, name='add_marks'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/admitcard/', views.student_admit_card, name='student_admit_card'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('custom_admin/allocate_user/', views.allocate_user, name='allocate_user'),
    path('custom_admin/users/', views.user_list, name='user_list'),
    path('custom_admin/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('custom_admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('student/result/', views.student_result, name='student_result'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('report_statistics/', views.report_statistics, name='report_statistics'),
    path('export_result_excel/<int:student_id>/', views.export_result_excel, name='export_result_excel'),
    path('change_password/', views.change_password, name='change_password'),
   
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)