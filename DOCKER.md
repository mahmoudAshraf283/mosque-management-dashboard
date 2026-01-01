# Mosque Management Dashboard - Docker Setup

This guide explains how to run the application using Docker.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Get Docker Compose](https://docs.docker.com/compose/install/))

## Quick Start

### 1. Build and Start All Services
```bash
cd /home/mahmoud/mosque
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- WhatsApp service (port 3000)
- Django application (port 8000)

### 2. Check Service Status
```bash
docker-compose ps
```

### 3. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f django
docker-compose logs -f whatsapp
docker-compose logs -f postgres
```

### 4. Authenticate WhatsApp
**Important:** You need to scan the QR code to link your WhatsApp account.

```bash
# View WhatsApp service logs to see QR code
docker-compose logs -f whatsapp
```

Scan the QR code with your WhatsApp mobile app:
1. Open WhatsApp → Settings → Linked Devices
2. Tap "Link a Device"
3. Scan the QR code displayed in the terminal

### 5. Access the Application
Open your browser: **http://localhost:8000**

## Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Stop and Remove Everything (including volumes)
```bash
docker-compose down -v
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Run Django Commands
```bash
# Create superuser
docker-compose exec django python manage.py createsuperuser

# Make migrations
docker-compose exec django python manage.py makemigrations

# Apply migrations
docker-compose exec django python manage.py migrate

# Send daily reminders (test mode)
docker-compose exec django python manage.py send_daily_reminders --test

# Send daily reminders (actual)
docker-compose exec django python manage.py send_daily_reminders
```

### Access Container Shell
```bash
# Django container
docker-compose exec django bash

# WhatsApp container
docker-compose exec whatsapp sh

# PostgreSQL container
docker-compose exec postgres psql -U postgres -d mosque_db
```

## Volumes

Docker volumes are used to persist data:

- **postgres_data**: PostgreSQL database files
- **whatsapp_auth**: WhatsApp authentication session (preserves login)
- **whatsapp_cache**: WhatsApp cache files
- **static_volume**: Django static files

## Environment Variables

You can customize the setup by modifying `docker-compose.yml`:

```yaml
environment:
  - DATABASE_HOST=postgres
  - DATABASE_PORT=5432
  - DATABASE_NAME=mosque_db
  - DATABASE_USER=postgres
  - DATABASE_PASSWORD=postgres  # Change this in production!
  - WHATSAPP_SERVICE_URL=http://whatsapp:3000
```

## Automated Daily Reminders

### Setup Cron on Host Machine

Since the containers are always running, you can set up a cron job on your host machine:

```bash
crontab -e
```

Add this line to send reminders at 6 AM daily:
```
0 6 * * * cd /home/mahmoud/mosque && docker-compose exec -T django python manage.py send_daily_reminders >> /home/mahmoud/mosque/logs/reminders.log 2>&1
```

## Troubleshooting

### WhatsApp QR Code Not Appearing
```bash
docker-compose logs whatsapp
```
Look for the QR code in the output.

### Database Connection Errors
```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U postgres

# Restart the database
docker-compose restart postgres
```

### Django Not Starting
```bash
# Check logs
docker-compose logs django

# Rebuild the container
docker-compose up -d --build django
```

### Clear All Data and Start Fresh
```bash
docker-compose down -v
docker-compose up -d
```

## Production Deployment

For production:

1. **Change PostgreSQL password** in `docker-compose.yml`
2. **Set DEBUG=False** in Django settings
3. **Use proper web server** (Gunicorn + Nginx)
4. **Enable HTTPS**
5. **Set up automatic backups** for PostgreSQL

## Network Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Browser    │─────▶│    Django    │─────▶│  PostgreSQL  │
│  :8000       │      │  Container   │      │  Container   │
└──────────────┘      └──────┬───────┘      └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │  WhatsApp    │
                      │   Service    │
                      │  Container   │
                      └──────────────┘
```

All containers are on the same Docker network and can communicate with each other.
