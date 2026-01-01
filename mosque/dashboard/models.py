from django.db import models
from django.utils.translation import gettext_lazy as _


class Mosque(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    address = models.TextField(_('Address'))
    phone = models.CharField(_('Phone'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('Mosque')
        verbose_name_plural = _('Mosques')

    def __str__(self):
        return self.name


class Imam(models.Model):
    COUNTRY_CODES = [
        ('+966', _('Saudi Arabia (+966)')),
        ('+971', _('UAE (+971)')),
        ('+965', _('Kuwait (+965)')),
        ('+973', _('Bahrain (+973)')),
        ('+974', _('Qatar (+974)')),
        ('+968', _('Oman (+968)')),
        ('+20', _('Egypt (+20)')),
        ('+962', _('Jordan (+962)')),
        ('+961', _('Lebanon (+961)')),
        ('+963', _('Syria (+963)')),
        ('+964', _('Iraq (+964)')),
        ('+967', _('Yemen (+967)')),
        ('+218', _('Libya (+218)')),
        ('+212', _('Morocco (+212)')),
        ('+213', _('Algeria (+213)')),
        ('+216', _('Tunisia (+216)')),
        ('+249', _('Sudan (+249)')),
        ('+1', _('USA/Canada (+1)')),
        ('+44', _('UK (+44)')),
    ]
    
    name = models.CharField(_('Name'), max_length=200)
    country_code = models.CharField(max_length=5, choices=COUNTRY_CODES, default='+966')
    phone = models.CharField(_('Phone'), max_length=20, help_text=_('WhatsApp number without country code'))
    email = models.EmailField(_('Email'), blank=True)

    class Meta:
        verbose_name = _('Caller')
        verbose_name_plural = _('Callers')

    def __str__(self):
        return self.name
    
    def get_full_phone(self):
        """Return full phone number with country code"""
        return f"{self.country_code}{self.phone}"


class Schedule(models.Model):
    WEEKDAY_CHOICES = [
        (0, _('Saturday')),
        (1, _('Sunday')),
        (2, _('Monday')),
        (3, _('Tuesday')),
        (4, _('Wednesday')),
        (5, _('Thursday')),
        (6, _('Friday')),
    ]
    
    PRAYER_TIME_CHOICES = [
        ('fajr', _('Fajr')),
        ('dhuhr', _('Dhuhr')),
        ('asr', _('Asr')),
        ('maghrib', _('Maghrib')),
        ('isha', _('Isha')),
    ]

    mosque = models.ForeignKey(Mosque, on_delete=models.CASCADE, verbose_name=_('Mosque'))
    imam = models.ForeignKey(Imam, on_delete=models.CASCADE, verbose_name=_('Imam'))
    weekday = models.IntegerField(_('Weekday'), choices=WEEKDAY_CHOICES)
    prayer_time = models.CharField(_('Prayer Time'), max_length=10, choices=PRAYER_TIME_CHOICES, default='dhuhr')
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')
        unique_together = ['mosque', 'weekday', 'prayer_time']

    def __str__(self):
        return f"{self.mosque.name} - {self.get_weekday_display()} - {self.get_prayer_time_display()}"
