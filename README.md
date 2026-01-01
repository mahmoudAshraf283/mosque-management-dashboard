# Mosque Management Dashboard

A comprehensive mosque and caller (Da'i) management system with automatic WhatsApp notifications

## ✨ Features

### 🕌 Core Management
- **Mosque Management**: Add and manage multiple mosques with addresses and contact info
- **Caller Management**: Manage Callers (Duʿāh/الدعاة) with WhatsApp numbers and country codes
- **Schedule Management**: Assign callers to 5 daily prayers (Fajr, Dhuhr, Asr, Maghrib, Isha)
- **Weekly Calendar**: Saturday-start week (Islamic week format)

### 📱 WhatsApp Integration
- **Personal WhatsApp**: Use your own phone number (via whatsapp-web.js)
- **Today's Schedule**: View today's appointments with one-click reminder button
- **Automatic Reminders**: Send WhatsApp messages on the actual prayer day
- **Smart Delays**: 2-5 minute random delays between messages (human-like behavior)
- **Notes Support**: Include custom notes (ملاحظات) in reminder messages
- **19 Country Codes**: Saudi Arabia (+966) as default, supports UAE, Kuwait, Egypt, etc.

### 🎨 User Interface
- **Fully Arabic**: 100% Arabic RTL interface (لوحة تحكم المساجد)
- **Professional Dark Theme**: Navy blue (#1e3a8a), dark gray (#334155), teal (#0891b2)
- **Responsive Design**: Bootstrap 5.1.3 RTL with Bootstrap Icons
- **Two Schedule Views**: 
  - **جدول اليوم** (Today's Schedule) - Current day with reminder button
  - **الجدول الأسبوعي** (Weekly Schedule) - Full week overview

### 🐳 Technology Stack
- **Backend**: Django 4.2.11 with PostgreSQL
- **Database**: PostgreSQL 15 (Docker container on port 5433)
- **WhatsApp**: Node.js with whatsapp-web.js
- **Frontend**: Bootstrap 5.1.3 RTL, Bootstrap Icons 1.11.0
- **Deployment**: Fully Dockerized (3-container architecture)
- **Session Persistence**: Docker volumes for WhatsApp authentication

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### 1. Start All Services
```bash
cd /home/mahmoud/mosque
docker-compose up -d
```

This starts 3 containers:
- **PostgreSQL** (port 5433) - Database
- **WhatsApp Service** (port 3000) - Node.js with whatsapp-web.js
- **Django App** (port 8000) - Web dashboard

### 2. Scan WhatsApp QR Code (First Time Only)
```bash
docker-compose logs -f whatsapp
```
Scan the QR code with WhatsApp on your phone. **The session persists - you only scan once!**

### 3. Access the Dashboard
Open browser: **http://localhost:8000**

### Stop Services
```bash
docker-compose down          # Stops containers, keeps data
docker-compose down -v       # Stops and deletes all data (including WhatsApp session!)
```

📖 **Full Docker documentation:** See [DOCKER.md](DOCKER.md)

---

## Manual Installation (Without Docker)

### 1. Install Python Dependencies
```bash
cd /home/mahmoud/mosque
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Database
```bash
cd mosque
python manage.py migrate
```

### 3. Start WhatsApp Service
```bash
cd /home/mahmoud/mosque/whatsapp_service
node server.js
```

**A QR Code will appear in the terminal - scan it with WhatsApp:**
1. Open WhatsApp on your phone
2. Go to Settings → Linked Devices
3. Tap "Link a Device"
4. Scan the QR Code

### 4. Start Django Server
In a new terminal:
```bash
cd /home/mahmoud/mosque
source venv/bin/activate
cd mosque
python manage.py runserver 0.0.0.0:8000
```

## 📖 Usage Guide

Open your browser at: **http://localhost:8000**

### Dashboard Pages

1. **الرئيسية (Home)** - Statistics and overview
2. **المساجد (Mosques)** - Manage mosques
3. **الدعاة (Callers)** - Manage callers (changed from Imam to Caller/Dāʿi)
4. **جدول اليوم (Today's Schedule)** - View today's appointments with "إرسال تذكيرات" button
5. **الجدول الأسبوعي (Weekly Schedule)** - Full week calendar view

### How to Send WhatsApp Reminders

#### Option 1: Today's Schedule Page (Recommended)
1. Navigate to **جدول اليوم** (Today's Schedule)
2. View all callers scheduled for today
3. Click **إرسال تذكيرات** (Send Reminders) button
4. All callers for today receive WhatsApp messages instantly

#### Option 2: Manual Command (Testing)
```bash
# Docker
docker-compose exec django python manage.py send_daily_reminders

# Without Docker
cd /home/mahmoud/mosque/mosque
python manage.py send_daily_reminders
```

#### Option 3: Automatic Daily Cron Job
Set up automatic reminders at 6 AM every day:

```bash
crontab -e
```

Add this line:
```
0 6 * * * cd /home/mahmoud/mosque && docker-compose exec -T django python manage.py send_daily_reminders >> /home/mahmoud/mosque/logs/reminders.log 2>&1
```

### WhatsApp Message Format

Messages sent to callers include:

```
السلام عليكم ورحمة الله وبركاته

تذكير: لديك موعد القاء كلمة اليوم
🕌 المسجد: [Mosque Name]
📍 الموقع: [Address]
📅 اليوم: [Weekday]
🕌 الصلاة: [Prayer Time]
📝 ملاحظات: [Notes - if available]

جزاك الله خيراً
```

**Smart Features:**
- 2-5 minute random delays between messages (appears human-sent)
- Only sends to registered WhatsApp numbers
- Notes (ملاحظات) included if added to schedule
- Messages sent only on the actual prayer day

---

## 🛠️ Manual Installation (Without Docker)

### 1. Install Python Dependencies
```bash
cd /home/mahmoud/mosque
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup PostgreSQL Database
Make sure PostgreSQL is running, then:
```bash
cd mosque
python manage.py migrate
```

### 3. Start WhatsApp Service
```bash
cd /home/mahmoud/mosque/whatsapp_service
npm install
node server.js
```

**Scan the QR Code** that appears with WhatsApp on your phone:
1. Open WhatsApp → Settings → Linked Devices
2. Tap "Link a Device"
3. Scan the QR Code

### 4. Start Django Server
In a new terminal:
```bash
cd /home/mahmoud/mosque
source venv/bin/activate
cd mosque
python manage.py runserver 0.0.0.0:8000
```

---

## 📊 Database Schema

### Models

**Mosque**
- name (CharField)
- address (TextField)
- phone (CharField)

**Imam (Caller/الداعي)**
- name (CharField)
- country_code (19 options, default: +966)
- phone (CharField)
- email (EmailField)

**Schedule**
- mosque (ForeignKey)
- imam (ForeignKey)
- weekday (IntegerField: 0=Saturday ... 6=Friday)
- prayer_time (CharField: fajr, dhuhr, asr, maghrib, isha)
- notes (TextField - included in WhatsApp messages)

---

## 🔧 Technology Details

### Docker Architecture
- **mosque_postgres**: PostgreSQL 15 Alpine (port 5433)
- **mosque_whatsapp**: Node.js 18 with whatsapp-web.js (port 3000)
- **mosque_django**: Python 3.12 with Django 4.2.11 (port 8000)

### Volumes
- `postgres_data`: Database persistence
- `whatsapp_auth`: WhatsApp session (QR code only once!)
- `whatsapp_cache`: WhatsApp cache
- `static_volume`: Django static files

### Python Dependencies
- Django 4.2.11
- psycopg2-binary 2.9.9 (PostgreSQL)
- requests 2.31.0 (HTTP calls to WhatsApp service)

### Node.js Dependencies
- whatsapp-web.js (WhatsApp Web client)
- qrcode-terminal (QR code display)
- express (HTTP server)

---

## ⚠️ Important Notes

- **WhatsApp Session**: Persists in Docker volume - scan QR code only once
- **Port 5433**: PostgreSQL uses 5433 (not default 5432) to avoid conflicts
- **Country Codes**: 19 countries supported, Saudi Arabia (+966) is default
- **Week Format**: Saturday-Friday (Islamic week format)
- **Terminology**: Changed from "Imam/الإمام" to "Caller/الداعي" (Dāʿi/Duʿāh)
- **Random Delays**: 2-5 minutes between messages to avoid spam detection
- **Notes Field**: Custom notes automatically included in WhatsApp messages

---

## 🐛 Troubleshooting

### WhatsApp not connecting
```bash
docker-compose logs whatsapp
# If QR code expired, restart:
docker-compose restart whatsapp
```

### Database connection error
```bash
# Check PostgreSQL is running:
docker-compose ps
docker-compose logs postgres
```

### Wrong day showing in Today's Schedule
- Make sure server date is correct
- Week starts on Saturday (0), ends on Friday (6)
- Thursday = weekday 5 in our system

### Clear all data and start fresh
```bash
docker-compose down -v  # ⚠️ Deletes everything including WhatsApp session!
docker-compose up -d
```

---

## 📝 License

Open source project for mosque management.

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
