# ==========================================
# APIS DE GESTIÓN DE HORARIOS ACADÉMICOS
# ==========================================

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from .models import (
    Schedule, Course, Subject, Classroom, TimeSlot, 
    AcademicYear, Grade, Student, SubjectAssignment,
    GradeSubjectAssignment
)
from authentication.models import StudentEnrollment


@csrf_exempt
def schedules_list_api(request):
    """API para listar horarios con filtros"""
    if request.method == 'GET':
        try:
            # Obtener parámetros de filtro
            course_id = request.GET.get('course_id')
            teacher_id = request.GET.get('teacher_id')
            classroom_id = request.GET.get('classroom_id')
            weekday = request.GET.get('weekday')
            time_slot_id = request.GET.get('time_slot_id')
            
            # Construir queryset base
            queryset = Schedule.objects.filter(is_active=True).select_related(
                'course__grade',
                'subject',
                'teacher__profile',
                'classroom',
                'time_slot',
                'academic_year'
            )
            
            # Aplicar filtros
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            if teacher_id:
                queryset = queryset.filter(teacher_id=teacher_id)
            if classroom_id:
                queryset = queryset.filter(classroom_id=classroom_id)
            if weekday:
                queryset = queryset.filter(weekday=weekday)
            if time_slot_id:
                queryset = queryset.filter(time_slot_id=time_slot_id)
            
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                queryset = queryset.filter(academic_year=current_year)
            
            schedules = queryset.order_by('weekday', 'time_slot__order')
            
            # Serializar datos
            schedules_data = []
            for schedule in schedules:
                schedules_data.append({
                    'id': schedule.id,
                    'weekday': schedule.weekday,
                    'weekday_name': schedule.get_weekday_display_full(),
                    'time_slot': {
                        'id': schedule.time_slot.id,
                        'name': schedule.time_slot.name,
                        'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                        'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                    },
                    'course': {
                        'id': schedule.course.id,
                        'name': str(schedule.course),
                        'grade_name': schedule.course.grade.name,
                        'section': schedule.course.section,
                    },
                    'subject': {
                        'id': schedule.subject.id,
                        'name': schedule.subject.name,
                        'area': schedule.subject.area,
                    },
                    'teacher': {
                        'id': schedule.teacher.id,
                        'name': schedule.teacher.get_full_name(),
                        'email': schedule.teacher.email,
                    },
                    'classroom': {
                        'id': schedule.classroom.id,
                        'name': schedule.classroom.name,
                        'code': schedule.classroom.code,
                        'capacity': schedule.classroom.capacity,
                    },
                    'notes': schedule.notes,
                    'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
                })
            
            return JsonResponse({
                'status': 'success',
                'data': schedules_data,
                'total': len(schedules_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener horarios: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt 
def schedule_resources_api(request):
    """API para obtener recursos necesarios para crear horarios"""
    if request.method == 'GET':
        try:
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            
            # Obtener cursos activos
            courses = Course.objects.filter(is_active=True).select_related('grade')
            courses_data = []
            for course in courses:
                courses_data.append({
                    'id': course.id,
                    'name': str(course),
                    'grade_name': course.grade.name,
                    'section': course.section,
                    'max_students': course.max_students,
                })
            
            # Obtener materias
            subjects = Subject.objects.all()
            subjects_data = []
            for subject in subjects:
                subjects_data.append({
                    'id': subject.id,
                    'name': subject.name,
                    'area': subject.area,
                    'code': subject.code,
                })
            
            # Obtener profesores activos
            teachers = User.objects.filter(
                profile__role='teacher', 
                is_active=True
            ).select_related('profile')
            teachers_data = []
            for teacher in teachers:
                teachers_data.append({
                    'id': teacher.id,
                    'name': teacher.get_full_name(),
                    'email': teacher.email,
                })
            
            # Obtener salones activos
            classrooms = Classroom.objects.filter(is_active=True)
            classrooms_data = []
            for classroom in classrooms:
                classrooms_data.append({
                    'id': classroom.id,
                    'name': classroom.name,
                    'code': classroom.code,
                    'capacity': classroom.capacity,
                    'building': classroom.building,
                    'floor': classroom.floor,
                })
            
            # Obtener franjas horarias activas
            time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
            time_slots_data = []
            for slot in time_slots:
                time_slots_data.append({
                    'id': slot.id,
                    'name': slot.name,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'order': slot.order,
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'courses': courses_data,
                    'subjects': subjects_data,
                    'teachers': teachers_data,
                    'classrooms': classrooms_data,
                    'time_slots': time_slots_data,
                    'weekdays': [
                        {'value': 1, 'name': 'Lunes'},
                        {'value': 2, 'name': 'Martes'},
                        {'value': 3, 'name': 'Miércoles'},
                        {'value': 4, 'name': 'Jueves'},
                        {'value': 5, 'name': 'Viernes'},
                    ],
                    'current_year': {
                        'id': current_year.id,
                        'name': current_year.name
                    } if current_year else None
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener recursos: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def create_schedule_api(request):
    """API para crear un nuevo horario"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validaciones básicas
            required_fields = ['course_id', 'subject_id', 'teacher_id', 'classroom_id', 'time_slot_id', 'weekday']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Campo requerido: {field}'
                    })
                
                # Verificar que el campo no esté vacío
                if not data[field] or str(data[field]).strip() == '':
                    field_names = {
                        'course_id': 'Curso',
                        'subject_id': 'Materia',
                        'teacher_id': 'Profesor',
                        'classroom_id': 'Salón',
                        'time_slot_id': 'Franja Horaria',
                        'weekday': 'Día de la semana'
                    }
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El campo {field_names.get(field, field)} es requerido y no puede estar vacío'
                    })
                
                # Verificar que los campos de ID sean números válidos
                if field.endswith('_id') or field == 'weekday':
                    try:
                        int(data[field])
                    except (ValueError, TypeError):
                        field_names = {
                            'course_id': 'Curso',
                            'subject_id': 'Materia', 
                            'teacher_id': 'Profesor',
                            'classroom_id': 'Salón',
                            'time_slot_id': 'Franja Horaria',
                            'weekday': 'Día de la semana'
                        }
                        return JsonResponse({
                            'status': 'error',
                            'message': f'El campo {field_names.get(field, field)} debe ser un número válido'
                        })
            
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay año académico activo'
                })
            
            # Verificar que los objetos existen
            try:
                course = Course.objects.get(id=data['course_id'])
                subject = Subject.objects.get(id=data['subject_id'])
                teacher = User.objects.get(id=data['teacher_id'], profile__role='teacher')
                classroom = Classroom.objects.get(id=data['classroom_id'])
                time_slot = TimeSlot.objects.get(id=data['time_slot_id'])
            except (Course.DoesNotExist, Subject.DoesNotExist, User.DoesNotExist, 
                    Classroom.DoesNotExist, TimeSlot.DoesNotExist) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Objeto no encontrado: {str(e)}'
                })
            
            # Validar conflictos de horario
            weekday_names = {
                1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes'
            }
            
            # 1. Verificar que el curso no tenga otra materia en ese horario
            if Schedule.objects.filter(
                course=course,
                time_slot=time_slot,
                weekday=data['weekday'],
                academic_year=current_year,
                is_active=True
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'El curso {course} ya tiene una clase en {time_slot.name} el {weekday_names[int(data["weekday"])]}'
                })
            
            # 2. Verificar que el profesor no esté en dos lugares al mismo tiempo
            if Schedule.objects.filter(
                teacher=teacher,
                time_slot=time_slot,
                weekday=data['weekday'],
                academic_year=current_year,
                is_active=True
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'El profesor {teacher.get_full_name()} ya tiene una clase en {time_slot.name} el {weekday_names[int(data["weekday"])]}'
                })
            
            # 3. Verificar que el salón no esté ocupado
            if Schedule.objects.filter(
                classroom=classroom,
                time_slot=time_slot,
                weekday=data['weekday'],
                academic_year=current_year,
                is_active=True
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'El salón {classroom.name} ya está ocupado en {time_slot.name} el {weekday_names[int(data["weekday"])]}'
                })
            
            # Crear el horario
            schedule = Schedule.objects.create(
                course=course,
                subject=subject,
                teacher=teacher,
                classroom=classroom,
                time_slot=time_slot,
                weekday=data['weekday'],
                academic_year=current_year,
                notes=data.get('notes', ''),
                created_by=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Horario creado exitosamente: {schedule}',
                'data': {
                    'id': schedule.id,
                    'schedule_summary': schedule.schedule_summary
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def schedule_detail_api(request, schedule_id):
    """API para obtener, actualizar o eliminar un horario específico"""
    try:
        schedule = Schedule.objects.select_related(
            'course__grade',
            'subject', 
            'teacher__profile',
            'classroom',
            'time_slot',
            'academic_year'
        ).get(id=schedule_id)
    except Schedule.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Horario no encontrado'
        })
    
    if request.method == 'GET':
        # Obtener detalles del horario
        schedule_data = {
            'id': schedule.id,
            'weekday': schedule.weekday,
            'weekday_name': schedule.get_weekday_display_full(),
            'time_slot': {
                'id': schedule.time_slot.id,
                'name': schedule.time_slot.name,
                'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
            },
            'course': {
                'id': schedule.course.id,
                'name': str(schedule.course),
                'grade_name': schedule.course.grade.name,
                'section': schedule.course.section,
            },
            'subject': {
                'id': schedule.subject.id,
                'name': schedule.subject.name,
                'area': schedule.subject.area,
            },
            'teacher': {
                'id': schedule.teacher.id,
                'name': schedule.teacher.get_full_name(),
                'email': schedule.teacher.email,
            },
            'classroom': {
                'id': schedule.classroom.id,
                'name': schedule.classroom.name,
                'code': schedule.classroom.code,
                'capacity': schedule.classroom.capacity,
            },
            'notes': schedule.notes,
            'is_active': schedule.is_active,
            'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
        }
        
        return JsonResponse({
            'status': 'success',
            'data': schedule_data
        })
    
    elif request.method == 'PUT':
        # Actualizar horario
        try:
            data = json.loads(request.body)
            
            # Campos que se pueden actualizar
            updatable_fields = ['subject_id', 'teacher_id', 'classroom_id', 'time_slot_id', 'weekday', 'notes']
            
            # Antes de actualizar, verificar conflictos si se cambian datos críticos
            critical_fields = ['teacher_id', 'classroom_id', 'time_slot_id', 'weekday']
            if any(field in data for field in critical_fields):
                # Obtener valores actualizados o mantener los existentes
                teacher_id = data.get('teacher_id', schedule.teacher.id)
                classroom_id = data.get('classroom_id', schedule.classroom.id)
                time_slot_id = data.get('time_slot_id', schedule.time_slot.id)
                weekday = data.get('weekday', schedule.weekday)
                
                # Verificar conflictos excluyendo el horario actual
                current_year = schedule.academic_year
                weekday_names = {
                    1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes'
                }
                
                # Conflicto de profesor
                teacher_conflict = Schedule.objects.filter(
                    teacher_id=teacher_id,
                    time_slot_id=time_slot_id,
                    weekday=weekday,
                    academic_year=current_year,
                    is_active=True
                ).exclude(id=schedule_id)
                
                if teacher_conflict.exists():
                    teacher = User.objects.get(id=teacher_id)
                    time_slot = TimeSlot.objects.get(id=time_slot_id)
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El profesor {teacher.get_full_name()} ya tiene una clase en {time_slot.name} el {weekday_names[int(weekday)]}'
                    })
                
                # Conflicto de salón
                classroom_conflict = Schedule.objects.filter(
                    classroom_id=classroom_id,
                    time_slot_id=time_slot_id,
                    weekday=weekday,
                    academic_year=current_year,
                    is_active=True
                ).exclude(id=schedule_id)
                
                if classroom_conflict.exists():
                    classroom = Classroom.objects.get(id=classroom_id)
                    time_slot = TimeSlot.objects.get(id=time_slot_id)
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El salón {classroom.name} ya está ocupado en {time_slot.name} el {weekday_names[int(weekday)]}'
                    })
            
            # Actualizar campos
            for field in updatable_fields:
                if field in data:
                    if field.endswith('_id'):
                        # Para campos de relación, obtener el objeto
                        model_name = field.replace('_id', '')
                        if model_name == 'subject':
                            setattr(schedule, model_name, Subject.objects.get(id=data[field]))
                        elif model_name == 'teacher':
                            setattr(schedule, model_name, User.objects.get(id=data[field]))
                        elif model_name == 'classroom':
                            setattr(schedule, model_name, Classroom.objects.get(id=data[field]))
                        elif model_name == 'time_slot':
                            setattr(schedule, model_name, TimeSlot.objects.get(id=data[field]))
                    else:
                        setattr(schedule, field, data[field])
            
            schedule.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Horario actualizado exitosamente',
                'data': {
                    'id': schedule.id,
                    'schedule_summary': schedule.schedule_summary
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            })
        except (Subject.DoesNotExist, User.DoesNotExist, Classroom.DoesNotExist, TimeSlot.DoesNotExist) as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Objeto no encontrado: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    elif request.method == 'DELETE':
        # Eliminar horario (soft delete)
        try:
            schedule.is_active = False
            schedule.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Horario eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al eliminar horario: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def schedule_matrix_api(request):
    """API para obtener la matriz de horarios (vista de calendario)"""
    if request.method == 'GET':
        try:
            # Obtener parámetros de filtro
            course_id = request.GET.get('course_id')
            teacher_id = request.GET.get('teacher_id')
            classroom_id = request.GET.get('classroom_id')
            
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay año académico activo'
                })
            
            # Construir queryset base
            queryset = Schedule.objects.filter(
                is_active=True,
                academic_year=current_year
            ).select_related(
                'course__grade',
                'subject',
                'teacher__profile',
                'classroom',
                'time_slot'
            )
            
            # Aplicar filtros
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            if teacher_id:
                queryset = queryset.filter(teacher_id=teacher_id)
            if classroom_id:
                queryset = queryset.filter(classroom_id=classroom_id)
            
            # Obtener todas las franjas horarias activas
            time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
            
            # Crear matriz de horarios
            weekdays = [1, 2, 3, 4, 5]  # Lunes a Viernes
            weekday_names = {
                1: 'Lunes',
                2: 'Martes', 
                3: 'Miércoles',
                4: 'Jueves',
                5: 'Viernes'
            }
            
            # Estructura de la matriz
            matrix = {}
            for time_slot in time_slots:
                matrix[time_slot.id] = {
                    'time_slot': {
                        'id': time_slot.id,
                        'name': time_slot.name,
                        'start_time': time_slot.start_time.strftime('%H:%M'),
                        'end_time': time_slot.end_time.strftime('%H:%M'),
                        'order': time_slot.order,
                    },
                    'days': {}
                }
                
                for weekday in weekdays:
                    matrix[time_slot.id]['days'][weekday] = {
                        'weekday': weekday,
                        'weekday_name': weekday_names[weekday],
                        'schedules': []
                    }
            
            # Llenar la matriz con los horarios
            schedules = queryset.order_by('weekday', 'time_slot__order')
            
            for schedule in schedules:
                if schedule.time_slot.id in matrix:
                    matrix[schedule.time_slot.id]['days'][schedule.weekday]['schedules'].append({
                        'id': schedule.id,
                        'course': {
                            'id': schedule.course.id,
                            'name': str(schedule.course),
                            'grade_name': schedule.course.grade.name,
                            'section': schedule.course.section,
                        },
                        'subject': {
                            'id': schedule.subject.id,
                            'name': schedule.subject.name,
                            'area': schedule.subject.area,
                        },
                        'teacher': {
                            'id': schedule.teacher.id,
                            'name': schedule.teacher.get_full_name(),
                        },
                        'classroom': {
                            'id': schedule.classroom.id,
                            'name': schedule.classroom.name,
                            'code': schedule.classroom.code,
                        },
                        'notes': schedule.notes,
                    })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'matrix': list(matrix.values()),
                    'weekdays': [{'value': k, 'name': v} for k, v in weekday_names.items()],
                    'total_schedules': schedules.count(),
                    'academic_year': current_year.name
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener matriz de horarios: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


# ==========================================
# APIS ADICIONALES PARA INTEGRACIÓN COMPLETA
# ==========================================

@csrf_exempt
def student_schedule_api(request):
    """API para obtener horario de un estudiante específico"""
    if request.method == 'GET':
        try:
            student_id = request.GET.get('student_id')
            if not student_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID de estudiante requerido'
                })
            
            # Obtener estudiante y su curso
            from .models import Student
            try:
                student = Student.objects.select_related('course', 'user').get(id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Estudiante no encontrado'
                })
            
            if not student.course:
                return JsonResponse({
                    'status': 'success',
                    'data': {
                        'student': {
                            'id': student.id,
                            'name': student.user.get_full_name(),
                            'student_id': student.student_id
                        },
                        'course': None,
                        'schedules': [],
                        'message': 'Estudiante no tiene curso asignado'
                    }
                })
            
            # Obtener horarios del curso del estudiante
            current_year = AcademicYear.objects.filter(is_current=True).first()
            schedules = Schedule.objects.filter(
                course=student.course,
                academic_year=current_year,
                is_active=True
            ).select_related(
                'subject', 'teacher', 'classroom', 'time_slot'
            ).order_by('weekday', 'time_slot__start_time')
            
            # Formatear datos
            schedule_data = []
            for schedule in schedules:
                schedule_data.append({
                    'id': schedule.id,
                    'weekday': schedule.weekday,
                    'weekday_name': schedule.get_weekday_display(),
                    'time_slot': {
                        'id': schedule.time_slot.id,
                        'name': schedule.time_slot.name,
                        'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                        'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                    },
                    'subject': {
                        'id': schedule.subject.id,
                        'name': schedule.subject.name,
                        'area': schedule.subject.area,
                    },
                    'teacher': {
                        'id': schedule.teacher.id,
                        'name': schedule.teacher.get_full_name(),
                    },
                    'classroom': {
                        'id': schedule.classroom.id,
                        'name': schedule.classroom.name,
                        'code': schedule.classroom.code,
                    }
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'student': {
                        'id': student.id,
                        'name': student.user.get_full_name(),
                        'student_id': student.student_id
                    },
                    'course': {
                        'id': student.course.id,
                        'name': str(student.course),
                        'grade': student.course.grade.name,
                        'section': student.course.section
                    },
                    'schedules': schedule_data,
                    'total_hours': len(schedule_data)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener horario del estudiante: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def teacher_schedule_api(request):
    """API para obtener horario de un profesor específico"""
    if request.method == 'GET':
        try:
            teacher_id = request.GET.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID de profesor requerido'
                })
            
            # Obtener profesor
            try:
                teacher = User.objects.get(id=teacher_id, profile__role='teacher')
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Profesor no encontrado'
                })
            
            # Obtener horarios del profesor
            current_year = AcademicYear.objects.filter(is_current=True).first()
            schedules = Schedule.objects.filter(
                teacher=teacher,
                academic_year=current_year,
                is_active=True
            ).select_related(
                'course__grade', 'subject', 'classroom', 'time_slot'
            ).order_by('weekday', 'time_slot__start_time')
            
            # Formatear datos
            schedule_data = []
            for schedule in schedules:
                schedule_data.append({
                    'id': schedule.id,
                    'weekday': schedule.weekday,
                    'weekday_name': schedule.get_weekday_display(),
                    'time_slot': {
                        'id': schedule.time_slot.id,
                        'name': schedule.time_slot.name,
                        'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                        'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                    },
                    'subject': {
                        'id': schedule.subject.id,
                        'name': schedule.subject.name,
                        'area': schedule.subject.area,
                    },
                    'course': {
                        'id': schedule.course.id,
                        'name': str(schedule.course),
                        'grade': schedule.course.grade.name,
                        'section': schedule.course.section,
                        'students_count': schedule.course.current_students_count
                    },
                    'classroom': {
                        'id': schedule.classroom.id,
                        'name': schedule.classroom.name,
                        'code': schedule.classroom.code,
                    }
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'teacher': {
                        'id': teacher.id,
                        'name': teacher.get_full_name(),
                    },
                    'schedules': schedule_data,
                    'total_hours': len(schedule_data),
                    'subjects_taught': list(set([s['subject']['name'] for s in schedule_data])),
                    'courses_taught': list(set([s['course']['name'] for s in schedule_data]))
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener horario del profesor: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def validate_schedule_conflicts_api(request):
    """API para validar conflictos de horarios antes de crear/actualizar"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            course_id = data.get('course_id')
            teacher_id = data.get('teacher_id')
            classroom_id = data.get('classroom_id')
            time_slot_id = data.get('time_slot_id')
            weekday = data.get('weekday')
            schedule_id = data.get('schedule_id')  # Para excluir en ediciones
            
            if not all([course_id, teacher_id, classroom_id, time_slot_id, weekday]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Todos los campos son requeridos'
                })
            
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay año académico activo'
                })
            
            conflicts = []
            
            # Verificar conflictos base
            base_filter = {
                'weekday': weekday,
                'time_slot_id': time_slot_id,
                'academic_year': current_year,
                'is_active': True
            }
            
            # Excluir el horario actual si estamos editando
            if schedule_id:
                base_filter['id__ne'] = schedule_id
            
            # Conflicto de profesor
            teacher_conflicts = Schedule.objects.filter(
                teacher_id=teacher_id,
                **base_filter
            ).select_related('course__grade', 'subject', 'classroom')
            
            for conflict in teacher_conflicts:
                conflicts.append({
                    'type': 'teacher',
                    'message': f'El profesor ya tiene clase de {conflict.subject.name} con {conflict.course} en {conflict.classroom.name}',
                    'schedule_id': conflict.id
                })
            
            # Conflicto de aula
            classroom_conflicts = Schedule.objects.filter(
                classroom_id=classroom_id,
                **base_filter
            ).select_related('course__grade', 'subject', 'teacher')
            
            for conflict in classroom_conflicts:
                conflicts.append({
                    'type': 'classroom',
                    'message': f'El salón ya está ocupado por {conflict.teacher.get_full_name()} con {conflict.course} para {conflict.subject.name}',
                    'schedule_id': conflict.id
                })
            
            # Conflicto de curso
            course_conflicts = Schedule.objects.filter(
                course_id=course_id,
                **base_filter
            ).select_related('subject', 'teacher', 'classroom')
            
            for conflict in course_conflicts:
                conflicts.append({
                    'type': 'course',
                    'message': f'El curso ya tiene clase de {conflict.subject.name} con {conflict.teacher.get_full_name()} en {conflict.classroom.name}',
                    'schedule_id': conflict.id
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'has_conflicts': len(conflicts) > 0,
                    'conflicts': conflicts,
                    'can_create': len(conflicts) == 0
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al validar conflictos: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def course_statistics_api(request):
    """API para obtener estadísticas de horarios por curso"""
    if request.method == 'GET':
        try:
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay año académico activo'
                })
            
            courses = Course.objects.filter(
                academic_year=current_year,
                is_active=True
            ).select_related('grade').prefetch_related('schedules', 'students')
            
            course_stats = []
            for course in courses:
                schedules = course.schedules.filter(is_active=True)
                subjects = schedules.values_list('subject__name', flat=True).distinct()
                teachers = schedules.values_list('teacher__first_name', 'teacher__last_name').distinct()
                
                course_stats.append({
                    'course': {
                        'id': course.id,
                        'name': str(course),
                        'grade': course.grade.name,
                        'section': course.section
                    },
                    'students_count': course.current_students_count,
                    'max_students': course.max_students,
                    'available_spots': course.available_spots,
                    'schedules_count': schedules.count(),
                    'subjects_count': len(subjects),
                    'teachers_count': len(teachers),
                    'subjects': list(subjects),
                    'teachers': [f"{fname} {lname}" for fname, lname in teachers],
                    'weekly_hours': schedules.count()  # Asumiendo 1 hora por slot
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'courses': course_stats,
                    'total_courses': len(course_stats),
                    'academic_year': current_year.name
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener estadísticas: {str(e)}'
            })


@csrf_exempt
def system_overview_api(request):
    """API para mostrar resumen general del sistema mejorado"""
    if request.method == 'GET':
        try:
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                current_year = AcademicYear.objects.first()
            
            if not current_year:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay año académico configurado'
                })
            
            # Estadísticas generales
            total_courses = Course.objects.filter(is_active=True).count()
            total_students = Student.objects.filter(status='active').count()
            total_teachers = User.objects.filter(profile__role='teacher', is_active=True).count()
            total_classrooms = Classroom.objects.filter(is_active=True).count()
            total_subjects = Subject.objects.count()
            total_time_slots = TimeSlot.objects.filter(is_active=True).count()
            
            # Estadísticas de horarios
            total_schedules = Schedule.objects.filter(
                is_active=True, 
                academic_year=current_year
            ).count()
            
            courses_with_schedules = Schedule.objects.filter(
                is_active=True, 
                academic_year=current_year
            ).values('course').distinct().count()
            
            # Estadísticas de asignaciones
            total_subject_assignments = SubjectAssignment.objects.filter(
                academic_year=current_year
            ).count()
            
            total_grade_assignments = GradeSubjectAssignment.objects.count()
            
            # Estadísticas de estudiantes
            students_with_course = Student.objects.filter(
                status='active', 
                course__isnull=False
            ).count()
            
            students_without_course = Student.objects.filter(
                status='active', 
                course__isnull=True
            ).count()
            
            # Uso de salones
            classrooms_in_use = Schedule.objects.filter(
                is_active=True, 
                academic_year=current_year
            ).values('classroom').distinct().count()
            
            # Calcular porcentajes
            course_coverage = (courses_with_schedules / total_courses * 100) if total_courses > 0 else 0
            enrollment_rate = (students_with_course / total_students * 100) if total_students > 0 else 0
            classroom_utilization = (classrooms_in_use / total_classrooms * 100) if total_classrooms > 0 else 0
            
            # Estadísticas por área de materia
            subject_areas = {}
            for subject in Subject.objects.all():
                area = subject.get_area_display()
                if area not in subject_areas:
                    subject_areas[area] = 0
                subject_areas[area] += 1
            
            # Top 5 salones más utilizados
            classroom_usage = (
                Schedule.objects.filter(is_active=True, academic_year=current_year)
                .values('classroom__name', 'classroom__capacity')
                .annotate(usage_count=Count('id'))
                .order_by('-usage_count')[:5]
            )
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'general_stats': {
                        'total_courses': total_courses,
                        'total_students': total_students,
                        'total_teachers': total_teachers,
                        'total_classrooms': total_classrooms,
                        'total_subjects': total_subjects,
                        'total_time_slots': total_time_slots
                    },
                    'schedule_stats': {
                        'total_schedules': total_schedules,
                        'courses_with_schedules': courses_with_schedules,
                        'course_coverage_percent': round(course_coverage, 1),
                        'subject_assignments': total_subject_assignments,
                        'grade_assignments': total_grade_assignments
                    },
                    'student_stats': {
                        'students_with_course': students_with_course,
                        'students_without_course': students_without_course,
                        'enrollment_rate_percent': round(enrollment_rate, 1)
                    },
                    'classroom_stats': {
                        'classrooms_in_use': classrooms_in_use,
                        'classroom_utilization_percent': round(classroom_utilization, 1),
                        'top_used_classrooms': list(classroom_usage)
                    },
                    'subject_areas': subject_areas,
                    'academic_year': current_year.name,
                    'improvements_summary': {
                        'system_status': 'Mejorado' if course_coverage > 40 else 'Necesita Mejoras',
                        'enrollment_status': 'Completo' if enrollment_rate >= 100 else 'Pendiente',
                        'classroom_efficiency': 'Alta' if classroom_utilization > 50 else 'Media' if classroom_utilization > 25 else 'Baja'
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener resumen del sistema: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})