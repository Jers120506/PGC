from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
import json

# Importar modelos básicos (temporalmente limpio)
from .models import AcademicYear, Grade, Subject, Course, GradeSubjectAssignment, Student
from authentication.models import User

# Importar vistas de horarios
from .schedule_views import (
    schedules_list_api, schedule_resources_api, create_schedule_api,
    schedule_detail_api, schedule_matrix_api
)

# Configurar logger
logger = logging.getLogger(__name__)


class AcademicDashboardView(LoginRequiredMixin, TemplateView):
    """Vista simplificada del dashboard académico"""
    template_name = 'academics_extended/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo datos básicos por ahora
        context.update({
            'total_academic_years': AcademicYear.objects.count(),
            'total_grades': Grade.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_courses': Course.objects.count(),
        })
        
        return context


class ScheduleManagementView(LoginRequiredMixin, TemplateView):
    """Vista para la gestión de horarios académicos"""
    template_name = 'academics_extended/schedule_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gestión de Horarios Académicos'
        return context


def academic_year_list_api(request):
    """API para listar años académicos"""
    academic_years = AcademicYear.objects.all().order_by('-start_date')
    data = []
    
    for year in academic_years:
        data.append({
            'id': year.id,
            'name': year.name,
            'start_date': year.start_date.isoformat(),
            'end_date': year.end_date.isoformat(),
            'is_current': year.is_current,
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })


def grade_list_api(request):
    """API para listar grados"""
    try:
        print("=== API grade_list_api llamada ===")
        print(f"Método: {request.method}")
        print(f"Usuario: {request.user}")
        print(f"Autenticado: {request.user.is_authenticated}")
        
        grades = Grade.objects.all().order_by('order')
        data = []
        
        for grade in grades:
            data.append({
                'id': grade.id,
                'name': grade.name,
                'level': grade.level,
                'level_display': grade.get_level_display(),
                'order': grade.order,
            })
        
        print(f"Grados encontrados: {len(data)}")
        
        response_data = {
            'status': 'success',
            'data': data,
            'count': len(data)
        }
        
        print(f"Respuesta: {response_data}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error en grade_list_api: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        })


def subject_list_api(request):
    """API para listar materias"""
    subjects = Subject.objects.all().order_by('area', 'name')
    data = []
    
    for subject in subjects:
        data.append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
            'area': subject.area,
            'area_display': subject.get_area_display(),
            'hours_per_week': subject.hours_per_week,
            'description': subject.description,
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })


# === APIs para gestión de Grados ===

@csrf_exempt
def create_grade_api(request):
    """API para crear un nuevo grado"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['name', 'level', 'order']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    })
            
            # Validar que el orden no esté duplicado
            if Grade.objects.filter(order=data['order']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe un grado con orden {data["order"]}'
                })
            
            # Crear el grado
            grade = Grade.objects.create(
                name=data['name'],
                level=data['level'],
                order=int(data['order'])
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Grado creado exitosamente',
                'data': {
                    'id': grade.id,
                    'name': grade.name,
                    'level': grade.level,
                    'level_display': grade.get_level_display(),
                    'order': grade.order
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
def grade_detail_api(request, grade_id):
    """API para obtener datos de un grado específico"""
    if request.method == 'GET':
        try:
            grade = Grade.objects.get(id=grade_id)
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': grade.id,
                    'name': grade.name,
                    'level': grade.level,
                    'order': grade.order
                }
            })
            
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Grado no encontrado'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def update_grade_api(request, grade_id):
    """API para actualizar un grado existente"""
    if request.method == 'POST':
        try:
            grade = Grade.objects.get(id=grade_id)
            import json
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['name', 'level', 'order']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    })
            
            # Validar que el orden no esté duplicado (excluyendo el grado actual)
            if Grade.objects.filter(order=data['order']).exclude(id=grade_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe un grado con orden {data["order"]}'
                })
            
            # Actualizar el grado
            grade.name = data['name']
            grade.level = data['level']
            grade.order = int(data['order'])
            grade.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Grado actualizado exitosamente',
                'data': {
                    'id': grade.id,
                    'name': grade.name,
                    'level': grade.level,
                    'level_display': grade.get_level_display(),
                    'order': grade.order
                }
            })
            
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Grado no encontrado'
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
def delete_grade_api(request, grade_id):
    """API para eliminar un grado"""
    if request.method == 'POST':
        try:
            grade = Grade.objects.get(id=grade_id)
            
            # Verificar si el grado tiene cursos asociados
            if hasattr(grade, 'course_set') and grade.course_set.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No se puede eliminar el grado porque tiene cursos asociados'
                })
            
            grade_name = grade.name
            grade.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Grado "{grade_name}" eliminado exitosamente'
            })
            
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Grado no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


# ================== APIs para Materias/Asignaturas ==================

@csrf_exempt
def subject_list_api(request):
    """API para listar todas las materias"""
    if request.method == 'GET':
        try:
            from .models import Subject
            
            logger.info(f"Cargando materias - Usuario: {request.user}, Autenticado: {request.user.is_authenticated}")
            
            subjects = Subject.objects.all().order_by('area', 'name')
            
            subjects_data = []
            for subject in subjects:
                subjects_data.append({
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'area': subject.area,
                    'area_display': subject.get_area_display(),
                    'hours_per_week': subject.hours_per_week,
                    'description': subject.description,
                })
            
            return JsonResponse({
                'status': 'success',
                'data': subjects_data,
                'count': len(subjects_data)
            })
            
        except Exception as e:
            logger.error(f"Error en subject_list_api: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def create_subject_api(request):
    """API para crear una nueva materia"""
    if request.method == 'POST':
        try:
            from .models import Subject
            import json
            
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['name', 'code', 'area', 'hours_per_week']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    })
            
            # Validar que el código no esté duplicado
            if Subject.objects.filter(code=data['code']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe una materia con código {data["code"]}'
                })
            
            # Validar horas por semana
            try:
                hours = int(data['hours_per_week'])
                if hours <= 0 or hours > 20:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Las horas por semana deben ser entre 1 y 20'
                    })
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Las horas por semana deben ser un número válido'
                })
            
            # Crear la materia
            subject = Subject.objects.create(
                name=data['name'],
                code=data['code'].upper(),
                area=data['area'],
                hours_per_week=hours,
                description=data.get('description', '')
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Materia creada exitosamente',
                'data': {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'area': subject.area,
                    'area_display': subject.get_area_display(),
                    'hours_per_week': subject.hours_per_week,
                    'description': subject.description,
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
def subject_detail_api(request, subject_id):
    """API para obtener datos de una materia específica"""
    if request.method == 'GET':
        try:
            subject = Subject.objects.get(id=subject_id)
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'area': subject.area,
                    'hours_per_week': subject.hours_per_week,
                    'description': subject.description or ''
                }
            })
            
        except Subject.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Materia no encontrada'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def update_subject_api(request, subject_id):
    """API para actualizar una materia existente"""
    if request.method == 'POST':
        try:
            from .models import Subject
            import json
            
            subject = Subject.objects.get(id=subject_id)
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['name', 'code', 'area', 'hours_per_week']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    })
            
            # Validar que el código no esté duplicado (excluyendo la materia actual)
            if Subject.objects.filter(code=data['code']).exclude(id=subject_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe una materia con código {data["code"]}'
                })
            
            # Validar horas por semana
            try:
                hours = int(data['hours_per_week'])
                if hours <= 0 or hours > 20:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Las horas por semana deben ser entre 1 y 20'
                    })
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Las horas por semana deben ser un número válido'
                })
            
            # Actualizar la materia
            subject.name = data['name']
            subject.code = data['code'].upper()
            subject.area = data['area']
            subject.hours_per_week = hours
            subject.description = data.get('description', '')
            subject.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Materia actualizada exitosamente',
                'data': {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'area': subject.area,
                    'area_display': subject.get_area_display(),
                    'hours_per_week': subject.hours_per_week,
                    'description': subject.description,
                }
            })
            
        except Subject.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Materia no encontrada'
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
def delete_subject_api(request, subject_id):
    """API para eliminar una materia"""
    if request.method == 'POST':
        try:
            from .models import Subject
            
            subject = Subject.objects.get(id=subject_id)
            
            # Verificar si la materia tiene asignaciones o cursos asociados
            if hasattr(subject, 'subjectassignment_set') and subject.subjectassignment_set.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No se puede eliminar la materia porque tiene asignaciones a cursos'
                })
            
            subject_name = subject.name
            subject.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Materia "{subject_name}" eliminada exitosamente'
            })
            
        except Subject.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Materia no encontrada'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
# APIs temporales para cursos - se añadirán al archivo views.py

# === COURSES CRUD API ===

@csrf_exempt
def course_list_api(request):
    """API para listar todos los cursos"""
    if request.method == 'GET':
        try:
            courses = Course.objects.select_related('grade', 'academic_year').all()
            courses_data = []
            
            for course in courses:
                courses_data.append({
                    'id': course.id,
                    'grade_id': course.grade.id,
                    'grade_name': course.grade.name,
                    'section': course.section,
                    'academic_year_id': course.academic_year.id,
                    'academic_year_name': course.academic_year.name,
                    'max_students': course.max_students,
                    'current_students_count': course.current_students_count,
                    'available_spots': course.available_spots,
                    'homeroom_teacher': course.homeroom_teacher.get_full_name() if course.homeroom_teacher else None,
                    'is_active': course.is_active
                })
            
            logger.info(f"Listados {len(courses_data)} cursos")
            return JsonResponse({
                'status': 'success',
                'data': courses_data,
                'count': len(courses_data)
            })
            
        except Exception as e:
            logger.error(f"Error al listar cursos: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener cursos: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def create_course_api(request):
    """API para crear un nuevo curso"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            grade_id = data.get('grade_id')
            section = data.get('section')
            academic_year_id = data.get('academic_year_id')
            max_students = data.get('max_students', 30)
            
            # Validaciones requeridas
            if not all([grade_id, section, academic_year_id]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Grado, sección y año académico son requeridos'
                })
            
            # Validar que el grado existe
            try:
                grade = Grade.objects.get(id=grade_id)
            except Grade.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El grado especificado no existe'
                })
            
            # Validar que el año académico existe
            try:
                academic_year = AcademicYear.objects.get(id=academic_year_id)
            except AcademicYear.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El año académico especificado no existe'
                })
            
            # Validar que la sección es válida
            valid_sections = [choice[0] for choice in Course.SECTION_CHOICES]
            if section not in valid_sections:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Sección inválida. Opciones válidas: {", ".join(valid_sections)}'
                })
            
            # Verificar que no existe ya un curso con la misma combinación
            if Course.objects.filter(
                grade=grade, 
                section=section, 
                academic_year=academic_year
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe un curso {grade.name} - {section} para el año {academic_year.name}'
                })
            
            # Crear el curso
            course = Course.objects.create(
                grade=grade,
                section=section,
                academic_year=academic_year,
                max_students=max_students
            )
            
            logger.info(f"Curso creado exitosamente: {course}")
            return JsonResponse({
                'status': 'success',
                'message': f'Curso {course} creado exitosamente',
                'course': {
                    'id': course.id,
                    'grade_name': course.grade.name,
                    'section': course.section,
                    'academic_year_name': course.academic_year.name,
                    'max_students': course.max_students,
                    'current_students_count': course.current_students_count,
                    'available_spots': course.available_spots,
                    'is_active': course.is_active
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            })
        except Exception as e:
            logger.error(f"Error al crear curso: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def update_course_api(request, course_id):
    """API para actualizar un curso existente"""
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            try:
                course = Course.objects.select_related('grade', 'academic_year').get(id=course_id)
            except Course.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Curso no encontrado'
                })
            
            # Actualizar campos si se proporcionan
            grade_id = data.get('grade_id')
            section = data.get('section')
            academic_year_id = data.get('academic_year_id')
            max_students = data.get('max_students')
            is_active = data.get('is_active')
            
            # Validar grado si se proporciona
            if grade_id is not None:
                try:
                    grade = Grade.objects.get(id=grade_id)
                    course.grade = grade
                except Grade.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El grado especificado no existe'
                    })
            
            # Validar año académico si se proporciona
            if academic_year_id is not None:
                try:
                    academic_year = AcademicYear.objects.get(id=academic_year_id)
                    course.academic_year = academic_year
                except AcademicYear.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El año académico especificado no existe'
                    })
            
            # Validar sección si se proporciona
            if section is not None:
                valid_sections = [choice[0] for choice in Course.SECTION_CHOICES]
                if section not in valid_sections:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Sección inválida. Opciones válidas: {", ".join(valid_sections)}'
                    })
                course.section = section
            
            # Validar número máximo de estudiantes
            if max_students is not None:
                if max_students < course.current_students_count:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'No se puede reducir el máximo a {max_students}. Estudiantes actuales: {course.current_students_count}'
                    })
                course.max_students = max_students
            
            # Actualizar estado activo si se proporciona
            if is_active is not None:
                course.is_active = is_active
            
            # Verificar unicidad antes de guardar (si se modificaron campos clave)
            if any([grade_id is not None, section is not None, academic_year_id is not None]):
                existing_course = Course.objects.filter(
                    grade=course.grade,
                    section=course.section,
                    academic_year=course.academic_year
                ).exclude(id=course.id)
                
                if existing_course.exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Ya existe un curso {course.grade.name} - {course.section} para el año {course.academic_year.name}'
                    })
            
            course.save()
            
            logger.info(f"Curso actualizado exitosamente: {course}")
            return JsonResponse({
                'status': 'success',
                'message': f'Curso {course} actualizado exitosamente',
                'course': {
                    'id': course.id,
                    'grade_name': course.grade.name,
                    'section': course.section,
                    'academic_year_name': course.academic_year.name,
                    'max_students': course.max_students,
                    'current_students_count': course.current_students_count,
                    'available_spots': course.available_spots,
                    'is_active': course.is_active
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            })
        except Exception as e:
            logger.error(f"Error al actualizar curso: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def delete_course_api(request, course_id):
    """API para eliminar un curso"""
    if request.method == 'DELETE':
        try:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Curso no encontrado'
                })
            
            # Verificar si tiene estudiantes asignados
            if course.current_students_count > 0:
                return JsonResponse({
                    'status': 'error',
                    'message': f'No se puede eliminar el curso. Tiene {course.current_students_count} estudiante(s) asignado(s)'
                })
            
            course_info = str(course)
            course.delete()
            
            logger.info(f"Curso eliminado exitosamente: {course_info}")
            return JsonResponse({
                'status': 'success',
                'message': f'Curso {course_info} eliminado exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error al eliminar curso: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
# APIs adicionales para asignaciones de materias a grados

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Grade, Subject, GradeSubjectAssignment

# ================== APIs PARA ASIGNACIONES DE MATERIAS A GRADOS ==================

@csrf_exempt
def grade_subject_assignments_api(request, grade_id):
    """API para obtener las materias asignadas a un grado específico"""
    if request.method == 'GET':
        try:
            grade = Grade.objects.get(id=grade_id)
            assignments = GradeSubjectAssignment.objects.filter(grade=grade).select_related('subject')
            
            assignments_data = []
            for assignment in assignments:
                assignments_data.append({
                    'id': assignment.id,
                    'subject_id': assignment.subject.id,
                    'subject_name': assignment.subject.name,
                    'subject_code': assignment.subject.code,
                    'subject_area': assignment.subject.area,
                    'subject_area_display': assignment.subject.get_area_display(),
                    'hours_per_week': assignment.hours_per_week,
                    'is_mandatory': assignment.is_mandatory,
                    'semester': assignment.semester,
                    'semester_display': assignment.get_semester_display(),
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'grade': {
                        'id': grade.id,
                        'name': grade.name,
                        'level': grade.level,
                    },
                    'assignments': assignments_data,
                    'total_hours': sum(a['hours_per_week'] for a in assignments_data),
                    'total_subjects': len(assignments_data)
                }
            })
            
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Grado no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def create_grade_subject_assignment_api(request):
    """API para crear una nueva asignación de materia a grado"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validaciones básicas
            required_fields = ['grade_id', 'subject_id', 'hours_per_week']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Campo requerido: {field}'
                    })
            
            # Verificar que el grado existe
            try:
                grade = Grade.objects.get(id=data['grade_id'])
            except Grade.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Grado no encontrado'
                })
            
            # Verificar que la materia existe
            try:
                subject = Subject.objects.get(id=data['subject_id'])
            except Subject.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Materia no encontrada'
                })
            
            # Verificar que no existe ya esta asignación
            semester = data.get('semester', 'anual')
            existing = GradeSubjectAssignment.objects.filter(
                grade=grade,
                subject=subject,
                semester=semester
            ).first()
            
            if existing:
                return JsonResponse({
                    'status': 'error',
                    'message': f'La materia {subject.name} ya está asignada a {grade.name} en el período {semester}'
                })
            
            # Crear la asignación
            assignment = GradeSubjectAssignment.objects.create(
                grade=grade,
                subject=subject,
                hours_per_week=data['hours_per_week'],
                is_mandatory=data.get('is_mandatory', True),
                semester=semester
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Materia {subject.name} asignada exitosamente a {grade.name}',
                'data': {
                    'id': assignment.id,
                    'subject_name': assignment.subject.name,
                    'grade_name': assignment.grade.name,
                    'hours_per_week': assignment.hours_per_week,
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
def update_grade_subject_assignment_api(request, assignment_id):
    """API para actualizar una asignación existente"""
    if request.method == 'POST':
        try:
            assignment = GradeSubjectAssignment.objects.get(id=assignment_id)
            data = json.loads(request.body)
            
            # Actualizar campos
            if 'hours_per_week' in data:
                assignment.hours_per_week = data['hours_per_week']
            if 'is_mandatory' in data:
                assignment.is_mandatory = data['is_mandatory']
            if 'semester' in data:
                assignment.semester = data['semester']
            
            assignment.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Asignación actualizada exitosamente',
                'data': {
                    'id': assignment.id,
                    'hours_per_week': assignment.hours_per_week,
                    'is_mandatory': assignment.is_mandatory,
                    'semester': assignment.semester,
                }
            })
            
        except GradeSubjectAssignment.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Asignación no encontrada'
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
def delete_grade_subject_assignment_api(request, assignment_id):
    """API para eliminar una asignación de materia a grado"""
    if request.method == 'POST':
        try:
            assignment = GradeSubjectAssignment.objects.get(id=assignment_id)
            
            # Guardar información para el mensaje
            assignment_info = f"{assignment.subject.name} de {assignment.grade.name}"
            
            # Eliminar la asignación
            assignment.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Asignación {assignment_info} eliminada exitosamente'
            })
            
        except GradeSubjectAssignment.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Asignación no encontrada'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def available_subjects_for_grade_api(request, grade_id):
    """API para obtener las materias disponibles para asignar a un grado"""
    if request.method == 'GET':
        try:
            grade = Grade.objects.get(id=grade_id)
            
            # Obtener materias ya asignadas
            assigned_subjects = GradeSubjectAssignment.objects.filter(
                grade=grade
            ).values_list('subject_id', flat=True)
            
            # Obtener materias disponibles (no asignadas)
            available_subjects = Subject.objects.exclude(
                id__in=assigned_subjects
            ).order_by('area', 'name')
            
            subjects_data = []
            for subject in available_subjects:
                subjects_data.append({
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'area': subject.area,
                    'area_display': subject.get_area_display(),
                    'hours_per_week': subject.hours_per_week,
                    'description': subject.description or ''
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'grade': {
                        'id': grade.id,
                        'name': grade.name,
                    },
                    'available_subjects': subjects_data,
                    'total_available': len(subjects_data)
                }
            })
            
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Grado no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
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
                    'phone': '',  # Campo no existe en el modelo
                    'birth_date': student.birth_date.strftime('%Y-%m-%d') if student.birth_date else '',
                    'course_id': student.course.id if student.course else None,
                    'course_name': str(student.course) if student.course else 'Sin asignar',
                    'grade_name': student.course.grade.name if student.course else 'Sin grado',
                    'status': student.status,
                    'status_display': student.get_status_display(),
                    'enrollment_date': student.enrollment_date.strftime('%Y-%m-%d'),
                    'guardian_name': student.guardian_name,
                    'guardian_phone': student.guardian_phone,
                    'address': student.address,
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
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            student = Student.objects.get(id=student_id)
            
            # Actualizar información del usuario
            if 'first_name' in data:
                student.user.first_name = data['first_name']
            if 'last_name' in data:
                student.user.last_name = data['last_name']
            if 'email' in data:
                student.user.email = data['email']
            
            # Actualizar información del estudiante
            if 'student_id' in data:
                student.student_id = data['student_id']
            if 'course_id' in data:
                if data['course_id']:
                    try:
                        course = Course.objects.get(id=data['course_id'])
                        student.course = course
                    except Course.DoesNotExist:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Curso no encontrado'
                        })
                else:
                    student.course = None
            
            if 'enrollment_date' in data:
                student.enrollment_date = data['enrollment_date']
            if 'birth_date' in data:
                student.birth_date = data['birth_date']
            if 'address' in data:
                student.address = data['address']
            if 'guardian_name' in data:
                student.guardian_name = data['guardian_name']
            if 'guardian_phone' in data:
                student.guardian_phone = data['guardian_phone']
            
            # Guardar cambios
            student.user.save()
            student.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Estudiante actualizado correctamente'
            })
            
        except Student.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Estudiante no encontrado'
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
    
    elif request.method == 'DELETE':
        try:
            student = Student.objects.get(id=student_id)
            user = student.user
            
            # Eliminar estudiante y usuario
            student.delete()
            user.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Estudiante eliminado correctamente'
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
