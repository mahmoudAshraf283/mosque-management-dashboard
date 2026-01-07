from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Mosque URLs
    path('mosques/', views.mosque_list, name='mosque_list'),
    path('mosques/schedules/', views.mosque_schedules, name='mosque_schedules'),
    path('mosques/send-weekly-reminders/', views.send_weekly_mosque_reminders, name='send_weekly_mosque_reminders'),
    path('mosques/create/', views.mosque_create, name='mosque_create'),
    path('mosques/<int:pk>/edit/', views.mosque_update, name='mosque_update'),
    path('mosques/<int:pk>/delete/', views.mosque_delete, name='mosque_delete'),
    path('mosques/notify/', views.send_mosque_notification, name='send_mosque_notification'),
    
    # Imam URLs
    path('imams/', views.imam_list, name='imam_list'),
    path('imams/create/', views.imam_create, name='imam_create'),
    path('imams/<int:pk>/edit/', views.imam_update, name='imam_update'),
    path('imams/<int:pk>/delete/', views.imam_delete, name='imam_delete'),
    
    # Schedule URLs
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/send-weekly-reminders/', views.send_weekly_reminders, name='send_weekly_reminders'),
    path('schedules/today/', views.today_schedule, name='today_schedule'),
    path('schedules/today/send-reminders/', views.send_today_reminders, name='send_today_reminders'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.schedule_update, name='schedule_update'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    
    # WhatsApp URLs
    path('whatsapp/qr/', views.whatsapp_qr, name='whatsapp_qr'),
]
