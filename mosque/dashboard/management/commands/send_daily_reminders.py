from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Schedule
from dashboard.whatsapp_web_service import WhatsAppWebService
import datetime
import time
import random
from hijri_converter import Gregorian


class Command(BaseCommand):
    help = 'Send WhatsApp notifications to imams for today\'s prayer schedules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - show what would be sent without actually sending',
        )

    def handle(self, *args, **options):
        test_mode = options['test']
        
        # Get today's weekday (0=Saturday in our model)
        today = datetime.datetime.now()
        weekday_map = {
            5: 0,  # Saturday
            6: 1,  # Sunday
            0: 2,  # Monday
            1: 3,  # Tuesday
            2: 4,  # Wednesday
            3: 5,  # Thursday
            4: 6,  # Friday
        }
        today_weekday = weekday_map[today.weekday()]
        
        # Get all schedules for today
        schedules = Schedule.objects.filter(weekday=today_weekday).select_related('mosque', 'imam')
        
        if not schedules.exists():
            self.stdout.write(self.style.WARNING('No schedules found for today.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {schedules.count()} schedule(s) for today'))
        
        # Initialize WhatsApp service
        whatsapp = WhatsAppWebService()
        
        if not test_mode and not whatsapp.is_ready():
            self.stdout.write(self.style.ERROR('WhatsApp service is not ready. Make sure it\'s running and authenticated.'))
            return
        
        # Send notifications
        sent_count = 0
        failed_count = 0
        total_schedules = schedules.count()
        
        for index, schedule in enumerate(schedules, 1):
            imam = schedule.imam
            mosque = schedule.mosque
            
            # Get prayer time and weekday in Arabic
            prayer_time_display = dict(Schedule.PRAYER_TIME_CHOICES).get(schedule.prayer_time)
            weekday_display = dict(Schedule.WEEKDAY_CHOICES).get(schedule.weekday)
            
            # Convert to Hijri date
            hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()
            hijri_months = [
                'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
                'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
            ]
            hijri_month_name = hijri_months[hijri_date.month - 1]
            hijri_date_str = f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"
            
            # Create message
            message = f"""السلام عليكم ورحمة الله وبركاته

تذكير: لديك موعد إلقاء كلمة اليوم
🕌 المسجد: {mosque.name}
📍 الموقع: {mosque.address}
📅 التاريخ: {hijri_date_str}
📅 اليوم: {weekday_display}
🕌 الصلاة: {prayer_time_display}"""
            
            # Add mosque phone number if available
            if mosque.phone:
                message += f"\n📞 هاتف المسجد: {mosque.phone}"
            
            message += "\n\nعند الانتهاء من إلقاء الكلمة يرجى إرسال رسالة:\n\"تم الانتهاء من إلقاء الكلمة\"\n\nجزاك الله خيراً"
            
            phone_number = imam.get_full_phone()
            
            if test_mode:
                self.stdout.write(self.style.WARNING(f'\n[TEST MODE] Would send to {imam.name} ({phone_number}):'))
                self.stdout.write(message)
                sent_count += 1
            else:
                # Send message
                success, response_message = whatsapp.send_message(phone_number, message)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f'✓ Sent to {imam.name} ({phone_number})'))
                    sent_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Failed to send to {imam.name}: {response_message}'))
                    failed_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        if test_mode:
            self.stdout.write(self.style.SUCCESS(f'Would send {sent_count} message(s)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully sent: {sent_count}'))
            if failed_count > 0:
                self.stdout.write(self.style.ERROR(f'Failed: {failed_count}'))
