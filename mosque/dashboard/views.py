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
    mosques = Mosque.objects.all().order_by('name')
    return render(request, 'dashboard/mosque_list.html', {'mosques': mosques})


def mosque_schedules(request):
    """Show mosques with schedules for selected day with tabs"""
    import datetime
    from hijri_converter import Gregorian
    
    # Get the target weekday (0=Saturday, 1=Sunday, etc.)
    # Default to current day
    today = datetime.datetime.now()
    weekday_map = {
        5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6,
    }
    current_weekday = weekday_map[today.weekday()]
    
    target_weekday = int(request.GET.get('weekday', current_weekday))
    
    # Calculate the target date based on weekday
    days_diff = (target_weekday - current_weekday) % 7
    target_date = today + datetime.timedelta(days=days_diff)
    
    # Get only mosques that have schedules for the target day
    mosques_with_schedules = Mosque.objects.filter(
        schedule__weekday=target_weekday
    ).distinct().order_by('name')
    
    # Get weekday display name
    weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(target_weekday)
    
    # Convert to Hijri
    hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
    hijri_months = ['', 'محرم', 'صفر', 'ربيع الأول', 'ربيع الثاني', 'جمادى الأولى', 'جمادى الآخرة', 
                    'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة']
    hijri_str = f"{hijri_date.day} {hijri_months[hijri_date.month]} {hijri_date.year}"
    
    return render(request, 'dashboard/mosque_schedules.html', {
        'mosques': mosques_with_schedules,
        'weekday_display': weekday_display,
        'hijri_date': hijri_str,
        'target_weekday': target_weekday,
    })


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


def send_mosque_notification(request):
    """Send WhatsApp notification to all mosques with schedules for the selected day"""
    import datetime
    from .whatsapp_web_service import WhatsAppWebService
    from hijri_converter import Gregorian
    
    if request.method != 'POST':
        return redirect('mosque_schedules')
    
    # Get the target weekday from POST data
    target_weekday = int(request.POST.get('target_weekday', 0))
    
    # Calculate the target date based on weekday
    today = datetime.datetime.now()
    weekday_map = {
        5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6,
    }
    current_weekday = weekday_map[today.weekday()]
    days_diff = (target_weekday - current_weekday) % 7
    target_date = today + datetime.timedelta(days=days_diff)
    
    # Get mosques that have schedules for the target day
    mosques_with_schedules = Mosque.objects.filter(
        schedule__weekday=target_weekday
    ).distinct()
    
    if not mosques_with_schedules.exists():
        messages.warning(request, 'لا توجد مساجد لديها جداول في هذا اليوم')
        return redirect(f'/mosques/schedules/?weekday={target_weekday}')
    
    # Initialize WhatsApp service
    whatsapp = WhatsAppWebService()
    
    if not whatsapp.is_ready():
        messages.error(request, 'خدمة واتساب غير جاهزة. يرجى التأكد من تشغيلها والمصادقة عليها.')
        return redirect(f'/mosques/schedules/?weekday={target_weekday}')
    
    # Convert to Hijri date
    hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
    hijri_months = [
        'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
        'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
    ]
    hijri_month_name = hijri_months[hijri_date.month - 1]
    hijri_date_str = f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"
    weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(target_weekday)
    
    # Send notifications to each mosque
    sent_count = 0
    failed_count = 0
    
    for mosque in mosques_with_schedules:
        if not mosque.get_full_phone():
            failed_count += 1
            continue
        
        # Get schedules for this mosque
        schedules = Schedule.objects.filter(
            mosque=mosque,
            weekday=target_weekday
        ).select_related('imam')
        
        # Create message
        message = f"""السلام عليكم ورحمة الله وبركاته

إشعار: لديكم كلمة يوم {weekday_display} في مسجد {mosque.name}
📅 التاريخ: {hijri_date_str}

الدعاة المقررون:
"""
        
        for schedule in schedules:
            prayer_time_display = dict(Schedule.PRAYER_TIME_CHOICES).get(schedule.prayer_time)
            message += f"\n🕌 {prayer_time_display}: {schedule.imam.name}"
            message += f"\n📞 رقم الداعية: {schedule.imam.get_full_phone()}"
            if schedule.notes:
                message += f"\n📝 ملاحظات: {schedule.notes}"
            message += "\n"
        
        # Add sender notes from form if available
        sender_notes = request.POST.get(f'mosque_notes_{mosque.id}', '').strip()
        if sender_notes:
            message += f"\n📝 ملاحظة إضافية: {sender_notes}\n"
        
        message += "\nجزاكم الله خيراً"
        
        # Send message
        phone_number = mosque.get_full_phone()
        success, response_message = whatsapp.send_message(phone_number, message)
        
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    # Show results
    if sent_count > 0:
        messages.success(request, _(f'تم إرسال {sent_count} إشعار بنجاح!'))
    if failed_count > 0:
        messages.warning(request, _(f'فشل إرسال {failed_count} إشعار.'))
    
    return redirect(f'/mosques/schedules/?weekday={target_weekday}')


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
    import datetime
    from hijri_converter import Gregorian
    
    # Get dates for each weekday
    today = datetime.date.today()
    current_weekday = (today.weekday() + 2) % 7  # Convert to our model (0=Saturday)
    
    weekday_dates = {}
    weekday_date_objects = {}
    hijri_months = [
        'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
        'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
    ]
    
    for weekday in range(7):
        days_diff = (weekday - current_weekday) % 7
        target_date = today + datetime.timedelta(days=days_diff)
        weekday_date_objects[weekday] = target_date
        hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
        hijri_month_name = hijri_months[hijri_date.month - 1]
        weekday_dates[weekday] = f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"
    
    # Get all schedules and sort by actual date
    schedules = list(Schedule.objects.select_related('mosque', 'imam').all())
    schedules.sort(key=lambda s: weekday_date_objects[s.weekday])
    
    schedule_by_day = {}
    for schedule in schedules:
        if schedule.weekday not in schedule_by_day:
            schedule_by_day[schedule.weekday] = []
        schedule_by_day[schedule.weekday].append(schedule)
    
    return render(request, 'dashboard/schedule_list.html', {
        'schedules': schedules,
        'schedule_by_day': schedule_by_day,
        'weekday_dates': weekday_dates,
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
    from hijri_converter import Gregorian
    
    # Get the target weekday (0=Saturday, 1=Sunday, etc.)
    # Default to current day
    today = datetime.datetime.now()
    weekday_map = {
        5: 0,  # Python Saturday → Our 0
        6: 1,  # Python Sunday → Our 1
        0: 2,  # Python Monday → Our 2
        1: 3,  # Python Tuesday → Our 3
        2: 4,  # Python Wednesday → Our 4
        3: 5,  # Python Thursday → Our 5
        4: 6,  # Python Friday → Our 6
    }
    current_weekday = weekday_map[today.weekday()]
    
    target_weekday = int(request.GET.get('weekday', current_weekday))
    
    # Calculate the target date based on weekday
    days_diff = (target_weekday - current_weekday) % 7
    target_date = today + datetime.timedelta(days=days_diff)
    
    # Get all schedules for the target day
    schedules = Schedule.objects.filter(weekday=target_weekday).select_related('mosque', 'imam').order_by('prayer_time')
    
    # Get day name
    weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(target_weekday)
    
    # Convert to Hijri
    hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
    hijri_months = ['', 'محرم', 'صفر', 'ربيع الأول', 'ربيع الثاني', 'جمادى الأولى', 'جمادى الآخرة', 
                    'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة']
    hijri_str = f"{hijri_date.day} {hijri_months[hijri_date.month]} {hijri_date.year}"
    
    context = {
        'schedules': schedules,
        'target_weekday': target_weekday,
        'weekday_display': weekday_display,
        'target_date': target_date.strftime('%Y-%m-%d'),
        'hijri_date': hijri_str,
    }
    return render(request, 'dashboard/today_schedule.html', context)


# Send reminders for today's schedules
def send_today_reminders(request):
    import datetime
    from .whatsapp_web_service import WhatsAppWebService
    from hijri_converter import Gregorian
    
    if request.method != 'POST':
        return redirect('today_schedule')
    
    # Get the target weekday from POST data
    target_weekday = int(request.POST.get('target_weekday', 0))
    
    # Calculate the target date based on weekday
    today = datetime.datetime.now()
    weekday_map = {
        5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6,
    }
    current_weekday = weekday_map[today.weekday()]
    days_diff = (target_weekday - current_weekday) % 7
    target_date = today + datetime.timedelta(days=days_diff)
    
    # Get all schedules for the target day
    schedules = Schedule.objects.filter(weekday=target_weekday).select_related('mosque', 'imam')
    
    if not schedules.exists():
        messages.warning(request, _('No schedules found for the selected day.'))
        return redirect(f'/schedules/today/?weekday={target_weekday}')
    
    # Initialize WhatsApp service
    whatsapp = WhatsAppWebService()
    
    if not whatsapp.is_ready():
        messages.error(request, _('WhatsApp service is not ready. Please make sure it is running and authenticated.'))
        return redirect(f'/schedules/today/?weekday={target_weekday}')
    
    # Send notifications
    sent_count = 0
    failed_count = 0
    
    for schedule in schedules:
        imam = schedule.imam
        mosque = schedule.mosque
        
        # Get prayer time and weekday in Arabic
        prayer_time_display = dict(Schedule.PRAYER_TIME_CHOICES).get(schedule.prayer_time)
        weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(schedule.weekday)
        
        # Convert to Hijri date
        hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
        hijri_months = [
            'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
            'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
        ]
        hijri_month_name = hijri_months[hijri_date.month - 1]
        hijri_date_str = f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"
        
        # Create message
        message = f"""السلام عليكم ورحمة الله وبركاته

تذكير: لديك موعد إلقاء كلمة يوم {weekday_display}
🕌 المسجد: {mosque.name}
📍 الموقع: {mosque.address}
📅 التاريخ الهجري: {hijri_date_str}
🕌 الصلاة: {prayer_time_display}"""
        
        # Add mosque phone number if available
        if mosque.phone:
            message += f"\n📞 هاتف المسجد: {mosque.get_full_phone()}"
        
        # Add schedule notes if available
        if schedule.notes:
            message += f"\n📝 ملاحظات: {schedule.notes}"
        
        # Add sender notes from form if available
        sender_notes = request.POST.get(f'notes_{schedule.id}', '').strip()
        if sender_notes:
            message += f"\n📝 ملاحظة إضافية: {sender_notes}"
        
        message += "\n\nعند الانتهاء من إلقاء الكلمة يرجى إرسال رسالة:\n\"تم الانتهاء من إلقاء الكلمة\"\n\nجزاك الله خيراً"
        
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
    
    return redirect(f'/schedules/today/?weekday={target_weekday}')


def send_weekly_reminders(request):
    """Send reminders to all imams in the weekly schedule with day and date"""
    import datetime
    from hijri_converter import Gregorian
    
    if request.method != 'POST':
        return redirect('schedule_list')
    
    # Get all schedules
    schedules = Schedule.objects.select_related('mosque', 'imam').all()
    
    if not schedules.exists():
        messages.warning(request, _('No schedules found to send reminders.'))
        return redirect('schedule_list')
    
    # Initialize WhatsApp service
    whatsapp = WhatsAppWebService()
    
    if not whatsapp.is_ready():
        messages.error(request, _('WhatsApp service is not ready. Please make sure it is running and authenticated.'))
        return redirect('schedule_list')
    
    # Calculate dates for each weekday
    today = datetime.datetime.now()
    current_weekday = (today.weekday() + 2) % 7  # Convert to our model (0=Saturday)
    
    hijri_months = [
        'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
        'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
    ]
    
    # Send notifications
    sent_count = 0
    failed_count = 0
    
    for schedule in schedules:
        imam = schedule.imam
        mosque = schedule.mosque
        
        # Calculate the target date for this schedule
        days_diff = (schedule.weekday - current_weekday) % 7
        target_date = today + datetime.timedelta(days=days_diff)
        
        # Get prayer time and weekday in Arabic
        prayer_time_display = dict(Schedule.PRAYER_TIME_CHOICES).get(schedule.prayer_time)
        weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(schedule.weekday)
        
        # Convert to Hijri date
        hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
        hijri_month_name = hijri_months[hijri_date.month - 1]
        hijri_date_str = f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"
        
        # Create message
        message = f"""السلام عليكم ورحمة الله وبركاته

تذكير: لديك موعد إلقاء كلمة يوم {weekday_display}
🕌 المسجد: {mosque.name}
📍 الموقع: {mosque.address}
📅 التاريخ الهجري: {hijri_date_str}
🕌 الصلاة: {prayer_time_display}"""
        
        # Add mosque phone number if available
        if mosque.phone:
            message += f"\n📞 هاتف المسجد: {mosque.get_full_phone()}"
        
        # Add schedule notes if available
        if schedule.notes:
            message += f"\n📝 ملاحظات: {schedule.notes}"
        
        message += "\n\nعند الانتهاء من إلقاء الكلمة يرجى إرسال رسالة:\n\"تم الانتهاء من إلقاء الكلمة\"\n\nجزاك الله خيراً"
        
        phone_number = imam.get_full_phone()
        
        # Send message
        success, response_message = whatsapp.send_message(phone_number, message)
        
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    # Show results
    if sent_count > 0:
        messages.success(request, _(f'Successfully sent {sent_count} reminder(s) to imams!'))
    if failed_count > 0:
        messages.warning(request, _(f'Failed to send {failed_count} reminder(s).'))
    
    return redirect('schedule_list')


def send_weekly_mosque_reminders(request):
    """Send weekly reminders to all mosques with their scheduled imams"""
    import datetime
    from hijri_converter import Gregorian
    
    if request.method != 'POST':
        return redirect('mosque_schedules')
    
    # Get all mosques that have schedules
    mosques_with_schedules = Mosque.objects.filter(schedule__isnull=False).distinct()
    
    if not mosques_with_schedules.exists():
        messages.warning(request, 'لا توجد مساجد لديها جداول')
        return redirect('mosque_schedules')
    
    # Initialize WhatsApp service
    whatsapp = WhatsAppWebService()
    
    if not whatsapp.is_ready():
        messages.error(request, 'خدمة واتساب غير جاهزة. يرجى التأكد من تشغيلها والمصادقة عليها.')
        return redirect('mosque_schedules')
    
    # Calculate dates for each weekday
    today = datetime.datetime.now()
    current_weekday = (today.weekday() + 2) % 7  # Convert to our model (0=Saturday)
    
    hijri_months = [
        'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
        'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
    ]
    
    # Send notifications
    sent_count = 0
    failed_count = 0
    
    for mosque in mosques_with_schedules:
        if not mosque.get_full_phone():
            failed_count += 1
            continue
        
        # Get all schedules for this mosque
        schedules = Schedule.objects.filter(mosque=mosque).select_related('imam')
        
        # Create message header
        message = f"""السلام عليكم ورحمة الله وبركاته

إشعار أسبوعي: الدعاة المقررون لمسجد {mosque.name}

"""
        
        # Group schedules by weekday
        schedule_by_day = {}
        for schedule in schedules:
            if schedule.weekday not in schedule_by_day:
                schedule_by_day[schedule.weekday] = []
            schedule_by_day[schedule.weekday].append(schedule)
        
        # Add each day's schedules
        for weekday in sorted(schedule_by_day.keys()):
            weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(weekday)
            
            # Calculate the target date for this weekday
            days_diff = (weekday - current_weekday) % 7
            target_date = today + datetime.timedelta(days=days_diff)
            
            # Convert to Hijri date
            hijri_date = Gregorian(target_date.year, target_date.month, target_date.day).to_hijri()
            hijri_month_name = hijri_months[hijri_date.month - 1]
            hijri_date_str = f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"
            
            message += f"📅 {weekday_display} - {hijri_date_str}\n"
            
            for schedule in schedule_by_day[weekday]:
                prayer_time_display = dict(Schedule.PRAYER_TIME_CHOICES).get(schedule.prayer_time)
                message += f"  🕌 {prayer_time_display}: {schedule.imam.name}\n"
                message += f"  📞 {schedule.imam.get_full_phone()}\n"
                if schedule.notes:
                    message += f"  📝 {schedule.notes}\n"
            message += "\n"
        
        message += "جزاكم الله خيراً"
        
        # Send message
        phone_number = mosque.get_full_phone()
        success, response_message = whatsapp.send_message(phone_number, message)
        
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    # Show results
    if sent_count > 0:
        messages.success(request, f'تم إرسال {sent_count} إشعار أسبوعي بنجاح!')
    if failed_count > 0:
        messages.warning(request, f'فشل إرسال {failed_count} إشعار.')
    
    return redirect('mosque_schedules')


def whatsapp_qr(request):
    """Display WhatsApp QR code for authentication"""
    whatsapp = WhatsAppWebService()
    qr_data = whatsapp.get_qr_code()
    
    context = {
        'qr_data': qr_data,
        'is_ready': whatsapp.is_ready()
    }
    return render(request, 'dashboard/whatsapp_qr.html', context)
