from django import forms
from .models import ProgramSchedule, Schedule

class ProgramScheduleForm(forms.ModelForm):
    class Meta:
        model = ProgramSchedule
        fields = ['instructor_name', 'course_code', 'course_name', 'credit_hours', 
                  'semester', 'program_name', 'program_code', 'room_number', 
                  'room_type', 'building_name', 'campus_name', 'year_level', 
                  'section', 'shift']
        
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['day', 'start_time', 'end_time']  # Assuming day, start_time, and end_time are in Schedule