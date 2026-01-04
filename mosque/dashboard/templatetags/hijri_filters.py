from django import template
from hijri_converter import Gregorian
import datetime

register = template.Library()

@register.filter
def to_hijri(date):
    """Convert Gregorian date to Hijri date string"""
    if not date:
        return ''
    
    if isinstance(date, datetime.datetime):
        date = date.date()
    
    hijri_date = Gregorian(date.year, date.month, date.day).to_hijri()
    hijri_months = [
        'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
        'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
    ]
    hijri_month_name = hijri_months[hijri_date.month - 1]
    return f"{hijri_date.day} {hijri_month_name} {hijri_date.year} هـ"

@register.simple_tag
def today_hijri():
    """Get today's date in Hijri"""
    today = datetime.date.today()
    return to_hijri(today)

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key, '')
