from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Mosque, Imam, Schedule
from .forms import MosqueForm, ImamForm, ScheduleForm
from .whatsapp_web_service import WhatsAppWebService


def dashboard(request):
    mosques = Mosque.objects.all()
    imams = Imam.objects.all()
    schedules = Schedule.objects.select_related('mosque', 'imam').all()
    
    # Group schedules by weekday
    schedule_by_day = {}
    for schedule in schedules:
        if schedule.weekday not in schedule_by_day:
            schedule_by_day[schedule.weekday] = []
        schedule_by_day[schedule.weekday].append(schedule)
    
    context = {
        'mosques': mosques,
        'imams': imams,
        'schedules': schedules,
        'schedule_by_day': schedule_by_day,
        'mosque_count': mosques.count(),
        'imam_count': imams.count(),
        'schedule_count': schedules.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


# Mosque Views
def mosque_list(request):
    mosques = Mosque.objects.all()
    return render(request, 'dashboard/mosque_list.html', {'mosques': mosques})


def mosque_create(request):
    if request.method == 'POST':
        form = MosqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Mosque added successfully!'))
            return redirect('mosque_list')
    else:
        form = MosqueForm()
    return render(request, 'dashboard/mosque_form.html', {'form': form, 'action': 'إضافة'})


def mosque_update(request, pk):
    mosque = get_object_or_404(Mosque, pk=pk)
    if request.method == 'POST':
        form = MosqueForm(request.POST, instance=mosque)
        if form.is_valid():
            form.save()
            messages.success(request, _('Mosque updated successfully!'))
            return redirect('mosque_list')
    else:
        form = MosqueForm(instance=mosque)
    return render(request, 'dashboard/mosque_form.html', {'form': form, 'action': 'تعديل'})


def mosque_delete(request, pk):
    mosque = get_object_or_404(Mosque, pk=pk)
    if request.method == 'POST':
        mosque.delete()
        messages.success(request, _('Mosque deleted successfully!'))
        return redirect('mosque_list')
    return render(request, 'dashboard/mosque_confirm_delete.html', {'mosque': mosque})


# Imam Views
def imam_list(request):
    imams = Imam.objects.all()
    return render(request, 'dashboard/imam_list.html', {'imams': imams})


def imam_create(request):
    if request.method == 'POST':
        form = ImamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Caller added successfully!'))
            return redirect('imam_list')
    else:
        form = ImamForm()
    return render(request, 'dashboard/imam_form.html', {'form': form, 'action': 'إضافة'})


def imam_update(request, pk):
    imam = get_object_or_404(Imam, pk=pk)
    if request.method == 'POST':
        form = ImamForm(request.POST, instance=imam)
        if form.is_valid():
            form.save()
            messages.success(request, _('Caller updated successfully!'))
            return redirect('imam_list')
    else:
        form = ImamForm(instance=imam)
    return render(request, 'dashboard/imam_form.html', {'form': form, 'action': 'تعديل'})


def imam_delete(request, pk):
    imam = get_object_or_404(Imam, pk=pk)
    if request.method == 'POST':
        imam.delete()
        messages.success(request, _('Caller deleted successfully!'))
        return redirect('imam_list')
    return render(request, 'dashboard/imam_confirm_delete.html', {'imam': imam})


# Schedule Views
def schedule_list(request):
    schedules = Schedule.objects.select_related('mosque', 'imam').order_by('weekday', 'prayer_time')
    
    schedule_by_day = {}
    for schedule in schedules:
        if schedule.weekday not in schedule_by_day:
            schedule_by_day[schedule.weekday] = []
        schedule_by_day[schedule.weekday].append(schedule)
    
    return render(request, 'dashboard/schedule_list.html', {
        'schedules': schedules,
        'schedule_by_day': schedule_by_day,
    })


def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, _('Schedule added successfully! Imam will receive WhatsApp reminder on the day of prayer.'))
            return redirect('schedule_list')
    else:
        form = ScheduleForm()
    return render(request, 'dashboard/schedule_form.html', {'form': form, 'action': 'إضافة'})


def schedule_update(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            updated_schedule = form.save()
            messages.success(request, _('Schedule updated successfully!'))
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'dashboard/schedule_form.html', {'form': form, 'action': 'تعديل'})


def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, _('Schedule deleted successfully!'))
        return redirect('schedule_list')
    return render(request, 'dashboard/schedule_confirm_delete.html', {'schedule': schedule})


# Today's Schedule View
def today_schedule(request):
    import datetime
    
    # Get today's weekday (0=Saturday in our model)
    today = datetime.datetime.now()
    # Python's weekday: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    # Our model: 0=Saturday, 1=Sunday, 2=Monday, 3=Tuesday, 4=Wednesday, 5=Thursday, 6=Friday
    weekday_map = {
        5: 0,  # Python Saturday → Our 0
        6: 1,  # Python Sunday → Our 1
        0: 2,  # Python Monday → Our 2
        1: 3,  # Python Tuesday → Our 3
        2: 4,  # Python Wednesday → Our 4
        3: 5,  # Python Thursday → Our 5
        4: 6,  # Python Friday → Our 6
    }
    today_weekday = weekday_map[today.weekday()]
    
    # Get all schedules for today
    schedules = Schedule.objects.filter(weekday=today_weekday).select_related('mosque', 'imam').order_by('prayer_time')
    
    # Get day name
    weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(today_weekday)
    
    context = {
        'schedules': schedules,
        'today_weekday': today_weekday,
        'weekday_display': weekday_display,
        'today_date': today.strftime('%Y-%m-%d'),
    }
    return render(request, 'dashboard/today_schedule.html', context)


# Send reminders for today's schedules
def send_today_reminders(request):
    import datetime
    from .whatsapp_web_service import WhatsAppWebService
    
    if request.method != 'POST':
        return redirect('today_schedule')
    
    # Get today's weekday
    today = datetime.datetime.now()
    # Python's weekday: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    # Our model: 0=Saturday, 1=Sunday, 2=Monday, 3=Tuesday, 4=Wednesday, 5=Thursday, 6=Friday
    weekday_map = {
        5: 0,  # Python Saturday → Our 0
        6: 1,  # Python Sunday → Our 1
        0: 2,  # Python Monday → Our 2
        1: 3,  # Python Tuesday → Our 3
        2: 4,  # Python Wednesday → Our 4
        3: 5,  # Python Thursday → Our 5
        4: 6,  # Python Friday → Our 6
    }
    today_weekday = weekday_map[today.weekday()]
    
    # Get all schedules for today
    schedules = Schedule.objects.filter(weekday=today_weekday).select_related('mosque', 'imam')
    
    if not schedules.exists():
        messages.warning(request, _('No schedules found for today.'))
        return redirect('today_schedule')
    
    # Initialize WhatsApp service
    whatsapp = WhatsAppWebService()
    
    if not whatsapp.is_ready():
        messages.error(request, _('WhatsApp service is not ready. Please make sure it is running and authenticated.'))
        return redirect('today_schedule')
    
    # Send notifications
    sent_count = 0
    failed_count = 0
    
    for schedule in schedules:
        imam = schedule.imam
        mosque = schedule.mosque
        
        # Get prayer time and weekday in Arabic
        prayer_time_display = dict(Schedule.PRAYER_TIME_CHOICES).get(schedule.prayer_time)
        weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(schedule.weekday)
        
        # Create message
        message = f"""السلام عليكم ورحمة الله وبركاته

تذكير: لديك موعد القاء كلمة اليوم
🕌 المسجد: {mosque.name}
📍 الموقع: {mosque.address}
📅 اليوم: {weekday_display}
🕌 الصلاة: {prayer_time_display}"""
        
        # Add notes if available
        if schedule.notes:
            message += f"\n📝 ملاحظات: {schedule.notes}"
        
        message += "\n\nجزاك الله خيراً"
        
        phone_number = imam.get_full_phone()
        
        # Send message
        success, response_message = whatsapp.send_message(phone_number, message)
        
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    # Show results
    if sent_count > 0:
        messages.success(request, _(f'Successfully sent {sent_count} reminder(s)!'))
    if failed_count > 0:
        messages.warning(request, _(f'Failed to send {failed_count} reminder(s).'))
    
    return redirect('today_schedule')

