#!/bin/bash

# Daily WhatsApp Reminder Script for Mosque Management
# This script should be run daily (e.g., at 6 AM) via cron

cd /home/mahmoud/mosque
source venv/bin/activate
cd mosque
python manage.py send_daily_reminders

# Log the execution
echo "$(date): Daily reminders sent" >> /home/mahmoud/mosque/logs/reminders.log
