from django import forms
from .models import Mosque, Imam, Schedule
from django.utils.translation import gettext_lazy as _


class MosqueForm(forms.ModelForm):
    name = forms.CharField(label=_('Mosque Name'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label=_('Address'), widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    phone = forms.CharField(label=_('Phone Number'), required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Mosque
        fields = ['name', 'address', 'phone']


class ImamForm(forms.ModelForm):
    name = forms.CharField(label=_('Caller Name'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    country_code = forms.ChoiceField(choices=Imam.COUNTRY_CODES, widget=forms.Select(attrs={'class': 'form-select'}))
    phone = forms.CharField(label=_('Phone (WhatsApp)'), widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 501234567'}))
    email = forms.EmailField(label=_('Email (optional)'), required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Imam
        fields = ['name', 'country_code', 'phone', 'email']


class ScheduleForm(forms.ModelForm):
    mosque = forms.ModelChoiceField(queryset=Mosque.objects.all(), label=_('Mosque'), widget=forms.Select(attrs={'class': 'form-select'}))
    imam = forms.ModelChoiceField(queryset=Imam.objects.all(), label=_('Caller'), widget=forms.Select(attrs={'class': 'form-select'}))
    weekday = forms.ChoiceField(choices=Schedule.WEEKDAY_CHOICES, label=_('Day of Week'), widget=forms.Select(attrs={'class': 'form-select'}))
    prayer_time = forms.ChoiceField(choices=Schedule.PRAYER_TIME_CHOICES, label=_('Prayer Time'), widget=forms.Select(attrs={'class': 'form-select'}))
    notes = forms.CharField(label=_('Notes (optional)'), required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = Schedule
        fields = ['mosque', 'imam', 'weekday', 'prayer_time', 'notes']
