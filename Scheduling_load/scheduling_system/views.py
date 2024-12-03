from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import InstructorData, InstructorCourse, Program, Room, Campus, Building, Room, ProgramSchedule, Schedule
from .forms import ProgramScheduleForm
from datetime import datetime
from django.utils import timezone


def home(request):
    return render(request, 'instructors_frontend/index.html')  # Original home page

# Create teaching load page
def create_teaching_load(request):
    return render(request, 'instructors_frontend/create_load.html')  # New page for teaching load

def teaching_load(request):
    return render(request,'instructors_frontend/teaching_load.html')

def section(request):
    return render(request,'instructors_frontend/section.html')

def search_instructors(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  # Get the search query
        filter_type = request.GET.get('filter', 'ALL')  # Get the filter type (ALL, regular, cos)

        # Debugging: Print query and filter
        print(f"Search Query: {query}, Filter: {filter_type}")

        # Start with all instructors
        instructors = InstructorData.objects.all()

        # Apply filtering logic based on employment type
        if filter_type == 'REGULAR':
            instructors = instructors.filter(employment_type='REGULAR')
        elif filter_type == 'COS':
            instructors = instructors.filter(employment_type='COS')

        # Apply query if present
        if query:
            # Split the query into parts (split by spaces)
            name_parts = query.split()

            # Dynamically build the query filters based on the parts
            filter_query = Q()

            for part in name_parts:
                filter_query |= Q(first_name__icontains=part) | Q(middle_initial__icontains=part) | Q(last_name__icontains=part)

            instructors = instructors.filter(filter_query)

        # Debugging: Print the number of instructors fetched
        print(f"Found {instructors.count()} instructors matching the query.")

        # Prepare the response for the search (as JSON for AJAX)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Prepare the list of instructor details to return
            data = [
                {
                    'name': f"{instructor.first_name} {instructor.middle_initial or ''} {instructor.last_name}".strip(),
                    'instructor_id': instructor.instructor_id,
                    'employment_type': instructor.employment_type,
                    'qualified_course': instructor.qualified_course,
                }
                for instructor in instructors
            ]



            return JsonResponse({'results': data})

        # For non-AJAX request, render the instructor list template
        return render(request, 'instructors_frontend/teaching_load.html', {
            'instructors': instructors,
            'filter': filter_type,  # Pass the employment type filter to the template
            'query': query,  # Pass the search query to the template
        })


def instructor_details(request):
    # Get 'id' from query parameters
    instructor_id = request.GET.get('id')

    # Ensure the 'id' is provided and is a valid integer
    if not instructor_id:
        return JsonResponse({'error': 'instructor_id is required'}, status=400)

    try:
        # Convert the instructor_id to an integer (this will raise ValueError if it's not a valid number)
        instructor_id = int(instructor_id)

        # Fetch the instructor record
        instructor = InstructorData.objects.get(instructor_id=instructor_id)

        # Prepare the instructor details to return as JSON
        data = {
            'instructor_id': instructor.instructor_id,
            'name': f"{instructor.first_name} {instructor.middle_initial or ''} {instructor.last_name}".strip(),
            'employment_type': instructor.employment_type,
            'qualified_courses': instructor.qualified_course,
        }

        return JsonResponse(data)

    except ValueError:
        # If 'id' is not a valid integer, return an error
        return JsonResponse({'error': 'Invalid instructor_id format, must be an integer'}, status=400)
    except InstructorData.DoesNotExist:
        # If no instructor is found with the given ID
        return JsonResponse({'error': 'Instructor data not found'}, status=404)

# List instructor courses
def instructor_course_list(request):
    courses = InstructorCourse.objects.all()
    return render(request, 'teaching_load.html', {'courses': courses})

def search_programs(request):
    query = request.GET.get('q', '')
    if query:
        programs = Program.objects.filter(program_name__icontains=query)
    else:
        programs = Program.objects.all()

    program_list = [
        {
            'program_id': program.program_id,
            'program_name': program.program_name,
            'program_code': program.program_code,
        }
        for program in programs
    ]

    return JsonResponse({'programs': program_list})

def program_details(request):
    program_id = request.GET.get('program_id', None)
    if program_id:
        try:
            program = Program.objects.get(program_id=program_id)
            program_data = {
                'program_id': program.program_id,
                'program_name': program.program_name,
                'program_code': program.program_code,
            }
            return JsonResponse({'program': program_data})
        except Program.DoesNotExist:
            return JsonResponse({'error': 'Program not found'}, status=404)
    else:
        return JsonResponse({'error': 'Program ID not provided'}, status=400)

def search_courses(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  # Get the query from request
        courses = InstructorCourse.objects.all()  # Start with all courses

        if query:  # Apply filtering if query exists
            query_parts = query.split()  # Split the query into parts for flexibility
            filter_query = Q()

            # Build the filter dynamically to search in course_code and course_name
            for part in query_parts:
                filter_query |= Q(course_code__icontains=part) | Q(course_name__icontains=part)

            courses = courses.filter(filter_query)  # Apply the filters

        # Prepare the response for suggestions
        data = [
            {
                'course_code': course.course_code,
                'course_name': course.course_name,
                'course_id': course.course_id,
            }
            for course in courses
        ]
        return JsonResponse({'results': data})  # Return the suggestions as JSON

def course_details(request):
    course_id = request.GET.get('id')

    if not course_id:
        return JsonResponse({'error': 'Course ID is required.'}, status=400)

    try:
        course = InstructorCourse.objects.get(course_id=course_id)

        data = {
            'course_id': course.course_id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'credit_hours': course.credit_hours,
            'semester': course.semester,
        }
        return JsonResponse(data)

    except InstructorCourse.DoesNotExist:
        return JsonResponse({'error': 'Course not found.'}, status=404)

def room_utilization(request):
    return render(request, 'instructors_frontend/room_util.html')  # Update path to match your template location

def search_rooms(request):
    query = request.GET.get('q', '')  # Search query, default to empty string
    building_name = request.GET.get('building', '')  # Optionally filter by building name
    campus_name = request.GET.get('campus', '')  # Optionally filter by campus name

    rooms = Room.objects.all()  # Start with all rooms

    if query:  # Filter by room number if query is provided
        rooms = rooms.filter(room_number__icontains=query)

    if building_name:  # Filter by building name if provided
        rooms = rooms.filter(building__building_name__icontains=building_name)

    if campus_name:  # Filter by campus name if provided
        rooms = rooms.filter(campus__campus_name__icontains=campus_name)

    # Limit to 10 rooms and return relevant data
    rooms_data = [{"room_id": room.room_id, "room_number": room.room_number, "room_type": room.room_type} for room in rooms[:10]]

    return JsonResponse({'rooms': rooms_data})


def room_details(request):
    room_id = request.GET.get('room_id')

    try:
        room = Room.objects.get(room_id=room_id)
        data = {
            'room': {
                'room_number': room.room_number,
                'room_type': room.room_type,
                'building_name': room.building.building_name,
                'campus_name': room.campus.campus_name,
            }
        }
        return JsonResponse(data)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
@csrf_exempt
def save_program_schedule(request):
    if request.method == "POST":

        # Print all request data for debugging
        print(request.POST)

        # Extract and validate required fields
        instructor_name = request.POST.get('instructor_name')
        if not instructor_name:
            return JsonResponse({"error": "Instructor name is required."}, status=400)
        bachelor_degree = request.POST.get('bachelor_degree',"")
        master_degree = request.POST.get('master_degree',"")

        # # Validate inputs
        # if not bachelor_degree:
        #     return JsonResponse({"error": "Bachelor's Degree is required."}, status=400)
        # if not master_degree:
        #     return JsonResponse({"error": "Master's Degree is required."}, status=400)

        course_code = request.POST.get('course_code')
        if not course_code:
            return JsonResponse({"error": "Course code is required."}, status=400)

        course_name = request.POST.get('course_name', "Untitled Course")
        
        credit_hours = request.POST.get('credit_hours')
        if credit_hours is None or not credit_hours.isdigit():
            return JsonResponse({"error": "Credit hours must be a valid integer."}, status=400)
        credit_hours = int(credit_hours)

        semester = request.POST.get('semester')
        program_name = request.POST.get('program_name')
        program_code = request.POST.get('program_code')
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        building_name = request.POST.get('building_name')   
        campus_name = request.POST.get('campus_name')

        year_level = request.POST.get('year_level')
        section = request.POST.get('section')
        shift = request.POST.get('shift')

        if not year_level:
            return JsonResponse({"error": "Year level is required."}, status=400)

         # Extracting all schedule entries
        schedule_days = []
        schedule_start_times = []
        schedule_end_times = []

        # Loop through all possible schedule indices (this assumes you have a finite, known upper limit of schedule entries, like 10)
        schedule_index = 0
        while True:
            day_key = f'schedules[{schedule_index}][day]'
            start_time_key = f'schedules[{schedule_index}][start_time]'
            end_time_key = f'schedules[{schedule_index}][end_time]'

            if day_key not in request.POST or start_time_key not in request.POST or end_time_key not in request.POST:
                break  # Exit the loop if we don't find any more schedules

            schedule_days.append(request.POST.get(day_key))
            schedule_start_times.append(request.POST.get(start_time_key))
            schedule_end_times.append(request.POST.get(end_time_key))

            schedule_index += 1

        if len(schedule_days) == 0:
            return JsonResponse({"error": "At least one schedule is required."}, status=400)

        # Loop through all the schedules and extract data
        for i in range(len(schedule_days)):
            day = schedule_days[i]
            start_time_str = schedule_start_times[i]
            end_time_str = schedule_end_times[i]

            # Validate day and time fields
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day not in valid_days:
                return JsonResponse({"error": f"Invalid day '{day}'. Must be one of {', '.join(valid_days)}."}, status=400)

            if not start_time_str or not end_time_str:
                return JsonResponse({"error": "Both start time and end time are required."}, status=400)

            try:
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
            except ValueError:
                return JsonResponse({"error": "Invalid time format. Use HH:MM."}, status=400)
    
            # Conflict detection with the Schedule model
            conflicts = Schedule.objects.filter(
                program_schedule__in=ProgramSchedule.objects.filter(
                    Q(instructor_name=instructor_name) | 
                    Q(room_number=room_number) |
                    (
                        Q(program_name=program_name) & 
                        Q(section=section) &
                        Q(year_level=year_level) &
                        Q(shift=shift)
                    )
                ),
                day=day,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            if conflicts.exists():
                conflict_details = conflicts.values(
                    'program_schedule__instructor_name', 
                    'program_schedule__course_code',
                    'program_schedule__room_number', 
                    'program_schedule__program_name',
                    'program_schedule__section',
                    'program_schedule__year_level',
                    'program_schedule__shift',
                    'day', 
                    'start_time', 
                    'end_time'
                )

                # Add a specific conflict message
                for conflict in conflict_details:
                        if conflict['program_schedule__instructor_name'] == instructor_name:
                            conflict['conflict_field'] = 'instructor_name'
                            conflict['conflict_message'] = "Instructor's schedule is already booked."
                        elif conflict['program_schedule__room_number'] == room_number:
                            conflict['conflict_field'] = 'room_number'
                            conflict['conflict_message'] = "Room schedule is already booked."
                        elif (
                            conflict['program_schedule__program_name'] == program_name and
                            conflict['program_schedule__section'] == section and
                            conflict['program_schedule__year_level'] == year_level and
                            conflict['program_schedule__shift'] == shift
                        ):
                            conflict['conflict_field'] = 'program_section_year_shift'
                            conflict['conflict_message'] = "Program, section, year level, or shift schedule is already booked."

                # Debug print to see the structure of conflict_details
                print(conflict_details)
                
                return JsonResponse({"conflict": True, "details": list(conflict_details)}, status=200)
        
        
        # Save data to the ProgramSchedule model
        program_schedule = ProgramSchedule.objects.create(
            instructor_name=instructor_name,
            course_code=course_code,
            course_name=course_name,
            credit_hours=credit_hours,
            semester=semester,
            program_name=program_name,
            program_code=program_code,
            room_number=room_number,
            room_type=room_type,
            building_name=building_name,
            campus_name=campus_name,
            year_level=year_level,
            section=section,
            shift=shift,
            bachelor_degree=bachelor_degree,  # Add this
            master_degree=master_degree       # Add this
        )# Create the associated Schedule entries
        for i in range(len(schedule_days)):
            day = schedule_days[i]
            start_time_str = schedule_start_times[i]
            end_time_str = schedule_end_times[i]
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

            # Create new Schedule entry for each schedule
            Schedule.objects.create(
                program_schedule=program_schedule,
                day=day,
                start_time=start_time,
                end_time=end_time
            )

        return JsonResponse({"message": "Program schedule saved successfully!"})
    else:
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)
    
# View to fetch rooms and semesters
def fetch_room_and_semester_data(request):
    try:
        # Fetch available room names
        rooms = Room.objects.all().values('room_number')  # Adjust the field name if necessary

        # Fetch available semesters
        semesters = ProgramSchedule.objects.values_list('semester', flat=True).distinct()

        # Prepare the data to return
        data = {
            'rooms': list(rooms),
            'semesters': list(semesters)
        }

        return JsonResponse(data, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
def fetch_timetable_for_room(request):
    room_number = request.GET.get('room_number')
    semester = request.GET.get('semester')

    if not room_number or not semester:
        return JsonResponse({"error": "Room number and semester are required."}, status=400)

    # Fetch timetable data based on room_number and semester
    timetable = ProgramSchedule.objects.filter(
        room_number=room_number,
        semester=semester
    )

    # Prepare timetable data with proper time conversion
    timetable_data = []
    for entry in timetable:
        try:
            # Convert start_time and end_time from text to datetime.time objects
            start_time_str = entry.start_time  # '08:00'
            end_time_str = entry.end_time     # '09:00'
            
            # Convert the string time to datetime.time objects
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

            timetable_data.append({
                'course_code': entry.course_code,
                'course_name': entry.course_name,
                'instructor_name': entry.instructor_name,
                'day': entry.day,
                'start_time': start_time.strftime('%H:%M'),  # Format the time for front-end
                'end_time': end_time.strftime('%H:%M'),
                'year_level': entry.year_level,
                'section': entry.section,
                'shift': entry.shift,
            })
        except Exception as e:
            print(f"Error processing timetable entry: {e}")

    return JsonResponse({'timetable': timetable_data})
