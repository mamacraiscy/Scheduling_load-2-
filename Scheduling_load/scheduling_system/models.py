from django.db import models


#DB fetching for instructors data
class InstructorData(models.Model):
    instructor_id = models.AutoField(primary_key=True)
    college_id = models.IntegerField(default=0)
    last_name = models.CharField(max_length=255, default="")
    first_name = models.CharField(max_length=255, default="")
    middle_initial = models.CharField(max_length=1, null=True, blank=True)
    employment_type = models.CharField(
        max_length=10, 
        choices=[('regular', 'Regular'), ('cos', 'COS')], 
        default='regular'
    )
    qualified_course = models.JSONField(default=dict)  
    availability_days = models.JSONField(default=list)  
    availability_times = models.JSONField(default=list)  

    class Meta:
      db_table = 'instructor'

    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.middle_initial or ''}"

#DB fetching for program ids
class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    college_id = models.IntegerField()
    program_code = models.TextField(null=True, blank=True)
    program_name = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'program'  

    def __str__(self):
        return f"{self.program_name} ({self.program_code})"

#DB fetching for courses / semester / credit_hours
class InstructorCourse(models.Model):
    course_id = models.AutoField(primary_key=True)
    program_id = models.IntegerField(default=0)
    course_code = models.TextField(null=True, blank=True)
    course_name = models.TextField(null=True, blank=True)
    department = models.TextField(null=True, blank=True)
    credit_hours = models.IntegerField(null=True, blank=True)
    prerequisites = models.JSONField(null=True, blank=True)
    school_year = models.TextField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'course'  

    def __str__(self):
        return f"{self.course_name} ({self.course_code}) - Semester {self.semester}"
    
    
class Campus(models.Model):
    campus_id = models.AutoField(primary_key=True)
    campus_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    class Meta:
        db_table = 'campus'

    def __str__(self):
        return self.campus_name

class Building(models.Model):
    building_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="buildings")  # ForeignKey to Campus
    building_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'building'

    def __str__(self):
        return self.building_name

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="rooms")  # ForeignKey to Building
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="rooms")  # ForeignKey to Campus
    room_number = models.CharField(max_length=255)
    room_type = models.CharField(max_length=255)
    availability_days = models.JSONField()
    availability_times = models.JSONField()

    class Meta:
        db_table = 'room'

    def __str__(self):
        return f"{self.room_number} - {self.room_type} in {self.building.building_name}, {self.campus.campus_name}"
    
# models.py
class ProgramSchedule(models.Model):
    # Instructor Information
    instructor_name = models.CharField(max_length=200)
    bachelor_degree = models.CharField(max_length=255, null=True, blank=True)
    master_degree = models.CharField(max_length=255, null=True, blank=True)
    # Course Information
    course_code = models.CharField(max_length=50)
    course_name = models.CharField(max_length=200)
    credit_hours = models.IntegerField(default=0)
    semester = models.CharField(max_length=50)

    # Program Information
    program_name = models.CharField(max_length=100)
    program_code = models.CharField(max_length=50)

    # Room Information
    room_number = models.CharField(max_length=100)
    room_type = models.CharField(max_length=50)  # Added room_type
    building_name = models.CharField(max_length=100)
    campus_name = models.CharField(max_length=100)

    # Program Level Information
    year_level = models.CharField(max_length=50)
    section = models.CharField(max_length=100)
    shift = models.CharField(max_length=20,)

    created_at = models.DateTimeField(auto_now_add=True)

    db_table = 'scheduling_system_programschedule'

    def __str__(self):
        return f"{self.instructor_name} - {self.course_name} - {self.program_name} - {self.room_number}"

# New Schedule model (Separate table for scheduling)
class Schedule(models.Model):
    # Foreign key linking to ProgramSchedule
    program_schedule = models.ForeignKey('ProgramSchedule', on_delete=models.CASCADE, related_name='schedules')

    # Scheduling Information
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'program_schedule'

    def __str__(self):
        return f"{self.day} - {self.start_time} to {self.end_time}"
