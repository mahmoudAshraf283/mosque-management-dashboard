from django import forms
from .models import Mosque, Imam, Schedule


class MosqueForm(forms.ModelForm):
    name = forms.CharField(label='اسم المسجد', widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label='العنوان', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    country_code = forms.ChoiceField(label='رمز الدولة', choices=Mosque.COUNTRY_CODES, widget=forms.Select(attrs={'class': 'form-select'}))
    phone = forms.CharField(label='رقم الهاتف', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'بدون رمز الدولة'}))

    class Meta:
        model = Mosque
        fields = ['name', 'address', 'country_code', 'phone']


class ImamForm(forms.ModelForm):
    name = forms.CharField(label='اسم الداعية', widget=forms.TextInput(attrs={'class': 'form-control'}))
    country_code = forms.ChoiceField(label='كود الدولة', choices=Imam.COUNTRY_CODES, widget=forms.Select(attrs={'class': 'form-select'}))
    phone = forms.CharField(label='الهاتف (واتساب)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 501234567'}))
    email = forms.EmailField(label='البريد الإلكتروني (اختياري)', required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Imam
        fields = ['name', 'country_code', 'phone', 'email']


class ScheduleForm(forms.ModelForm):
    mosque = forms.ModelChoiceField(queryset=Mosque.objects.all(), label='المسجد', widget=forms.Select(attrs={'class': 'form-select'}))
    imam = forms.ModelChoiceField(queryset=Imam.objects.all(), label='الداعية', widget=forms.Select(attrs={'class': 'form-select'}))
    weekday = forms.ChoiceField(choices=Schedule.WEEKDAY_CHOICES, label='يوم الأسبوع', widget=forms.Select(attrs={'class': 'form-select'}))
    prayer_time = forms.ChoiceField(choices=Schedule.PRAYER_TIME_CHOICES, label='وقت الصلاة', widget=forms.Select(attrs={'class': 'form-select'}))
    notes = forms.CharField(label='ملاحظات (اختياري)', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = Schedule
        fields = ['mosque', 'imam', 'weekday', 'prayer_time', 'notes']
