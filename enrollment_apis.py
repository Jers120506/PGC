# APIs para el sistema de inscripciones de estudiantes

# ================== APIs PARA SISTEMA DE INSCRIPCIONES ==================

@csrf_exempt
def students_list_api(request):
    """API para obtener lista de estudiantes"""
    if request.method == 'GET':
        try:
            students = Student.objects.select_related('user', 'course', 'course__grade').all()
            
            students_data = []
            for student in students:
                students_data.append({
                    'id': student.id,
                    'student_id': student.student_id,
                    'full_name': student.user.get_full_name(),
                    'first_name': student.user.first_name,
                    'last_name': student.user.last_name,
                    'email': student.user.email,
                    'course_id': student.course.id if student.course else None,
                    'course_name': str(student.course) if student.course else 'Sin asignar',
                    'grade_name': student.course.grade.name if student.course else 'Sin grado',
                    'status': student.status,
                    'status_display': student.get_status_display(),
                    'enrollment_date': student.enrollment_date.strftime('%Y-%m-%d'),
                    'guardian_name': student.guardian_name,
                    'guardian_phone': student.guardian_phone,
                    'age': student.age,
                })
            
            return JsonResponse({
                'status': 'success',
                'data': students_data,
                'total': len(students_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def courses_with_availability_api(request):
    """API para obtener cursos con información de disponibilidad"""
    if request.method == 'GET':
        try:
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                current_year = AcademicYear.objects.first()
            
            if not current_year:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay años académicos configurados'
                })
            
            courses = Course.objects.filter(
                academic_year=current_year,
                is_active=True
            ).select_related('grade').prefetch_related('students')
            
            courses_data = []
            for course in courses:
                current_students = course.current_students_count
                available_spots = course.available_spots
                
                courses_data.append({
                    'id': course.id,
                    'name': str(course),
                    'grade_name': course.grade.name,
                    'grade_level': course.grade.level,
                    'section': course.section,
                    'max_students': course.max_students,
                    'current_students': current_students,
                    'available_spots': available_spots,
                    'is_full': available_spots <= 0,
                    'homeroom_teacher': course.homeroom_teacher.get_full_name() if course.homeroom_teacher else 'No asignado',
                    'academic_year': current_year.name,
                })
            
            return JsonResponse({
                'status': 'success',
                'data': courses_data,
                'total': len(courses_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def create_student_api(request):
    """API para crear un nuevo estudiante"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validaciones básicas
            required_fields = [
                'first_name', 'last_name', 'email', 'student_id',
                'enrollment_date', 'guardian_name', 'guardian_phone',
                'address', 'birth_date'
            ]
            
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Campo requerido: {field}'
                    })
            
            # Verificar que el email no esté en uso
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'El email ya está en uso'
                })
            
            # Verificar que el student_id no esté en uso
            if Student.objects.filter(student_id=data['student_id']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'El ID de estudiante ya está en uso'
                })
            
            # Crear usuario
            user = User.objects.create_user(
                username=data['student_id'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password='temporal123'  # Contraseña temporal
            )
            
            # Crear perfil de estudiante
            student = Student.objects.create(
                user=user,
                student_id=data['student_id'],
                enrollment_date=data['enrollment_date'],
                guardian_name=data['guardian_name'],
                guardian_phone=data['guardian_phone'],
                guardian_email=data.get('guardian_email', ''),
                guardian_relationship=data.get('guardian_relationship', 'Padre/Madre'),
                address=data['address'],
                birth_date=data['birth_date'],
                birth_place=data.get('birth_place', ''),
                medical_info=data.get('medical_info', ''),
                status='active'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Estudiante {student.user.get_full_name()} creado exitosamente',
                'data': {
                    'id': student.id,
                    'student_id': student.student_id,
                    'full_name': student.user.get_full_name(),
                    'email': student.user.email,
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
def enroll_student_api(request):
    """API para inscribir un estudiante en un curso"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validaciones básicas
            if 'student_id' not in data or 'course_id' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren student_id y course_id'
                })
            
            # Verificar que el estudiante existe
            try:
                student = Student.objects.get(id=data['student_id'])
            except Student.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Estudiante no encontrado'
                })
            
            # Verificar que el curso existe
            try:
                course = Course.objects.get(id=data['course_id'])
            except Course.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Curso no encontrado'
                })
            
            # Verificar que el curso tiene cupos disponibles
            if course.available_spots <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': f'El curso {course} no tiene cupos disponibles'
                })
            
            # Verificar que el estudiante no esté ya inscrito en otro curso del mismo año académico
            existing_enrollment = Student.objects.filter(
                user=student.user,
                course__academic_year=course.academic_year
            ).exclude(id=student.id).first()
            
            if existing_enrollment:
                return JsonResponse({
                    'status': 'error',
                    'message': f'El estudiante ya está inscrito en {existing_enrollment.course} para el año {course.academic_year.name}'
                })
            
            # Realizar la inscripción
            student.course = course
            student.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Estudiante {student.user.get_full_name()} inscrito exitosamente en {course}',
                'data': {
                    'student_name': student.user.get_full_name(),
                    'course_name': str(course),
                    'remaining_spots': course.available_spots,
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
def unenroll_student_api(request):
    """API para desinscribir un estudiante de un curso"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validaciones básicas
            if 'student_id' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requiere student_id'
                })
            
            # Verificar que el estudiante existe
            try:
                student = Student.objects.get(id=data['student_id'])
            except Student.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Estudiante no encontrado'
                })
            
            if not student.course:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El estudiante no está inscrito en ningún curso'
                })
            
            # Guardar información del curso para el mensaje
            course_name = str(student.course)
            
            # Desinscribir al estudiante
            student.course = None
            student.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Estudiante {student.user.get_full_name()} desinscrito de {course_name}',
                'data': {
                    'student_name': student.user.get_full_name(),
                    'former_course': course_name,
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
def student_detail_api(request, student_id):
    """API para obtener detalles de un estudiante específico"""
    if request.method == 'GET':
        try:
            student = Student.objects.select_related('user', 'course', 'course__grade').get(id=student_id)
            
            data = {
                'id': student.id,
                'student_id': student.student_id,
                'user_info': {
                    'first_name': student.user.first_name,
                    'last_name': student.user.last_name,
                    'email': student.user.email,
                    'full_name': student.user.get_full_name(),
                },
                'course_info': {
                    'id': student.course.id if student.course else None,
                    'name': str(student.course) if student.course else 'Sin asignar',
                    'grade_name': student.course.grade.name if student.course else 'Sin grado',
                    'section': student.course.section if student.course else None,
                } if student.course else None,
                'personal_info': {
                    'enrollment_date': student.enrollment_date.strftime('%Y-%m-%d'),
                    'birth_date': student.birth_date.strftime('%Y-%m-%d'),
                    'birth_place': student.birth_place,
                    'age': student.age,
                    'address': student.address,
                    'status': student.status,
                    'status_display': student.get_status_display(),
                    'medical_info': student.medical_info,
                },
                'guardian_info': {
                    'name': student.guardian_name,
                    'phone': student.guardian_phone,
                    'email': student.guardian_email,
                    'relationship': student.guardian_relationship,
                }
            }
            
            return JsonResponse({
                'status': 'success',
                'data': data
            })
            
        except Student.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def enrollment_statistics_api(request):
    """API para obtener estadísticas de inscripciones"""
    if request.method == 'GET':
        try:
            # Obtener año académico actual
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if not current_year:
                current_year = AcademicYear.objects.first()
            
            total_students = Student.objects.filter(status='active').count()
            enrolled_students = Student.objects.filter(
                status='active',
                course__isnull=False,
                course__academic_year=current_year
            ).count() if current_year else 0
            
            pending_students = total_students - enrolled_students
            
            # Estadísticas por grado
            grade_stats = []
            if current_year:
                courses = Course.objects.filter(academic_year=current_year, is_active=True)
                grade_data = {}
                
                for course in courses:
                    grade_name = course.grade.name
                    if grade_name not in grade_data:
                        grade_data[grade_name] = {
                            'total_capacity': 0,
                            'enrolled': 0,
                            'courses': 0
                        }
                    
                    grade_data[grade_name]['total_capacity'] += course.max_students
                    grade_data[grade_name]['enrolled'] += course.current_students_count
                    grade_data[grade_name]['courses'] += 1
                
                for grade_name, stats in grade_data.items():
                    grade_stats.append({
                        'grade_name': grade_name,
                        'total_capacity': stats['total_capacity'],
                        'enrolled': stats['enrolled'],
                        'available': stats['total_capacity'] - stats['enrolled'],
                        'courses_count': stats['courses'],
                        'occupancy_rate': round((stats['enrolled'] / stats['total_capacity']) * 100, 1) if stats['total_capacity'] > 0 else 0
                    })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'overview': {
                        'total_students': total_students,
                        'enrolled_students': enrolled_students,
                        'pending_students': pending_students,
                        'enrollment_rate': round((enrolled_students / total_students) * 100, 1) if total_students > 0 else 0,
                        'academic_year': current_year.name if current_year else 'No definido'
                    },
                    'grade_statistics': grade_stats
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})