from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

# Importar modelos b√°sicos (temporalmente limpio)
from .models import AcademicYear, Grade, Subject, Course
from authentication.models import User

# Configurar logger
logger = logging.getLogger(__name__)


class AcademicDashboardView(LoginRequiredMixin, TemplateView):
    """Vista simplificada del dashboard acad√©mico"""
    template_name = 'academics_extended/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo datos b√°sicos por ahora
        context.update({
            'total_academic_years': AcademicYear.objects.count(),
            'total_grades': Grade.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_courses': Course.objects.count(),
        })
        
        return context


def academic_year_list_api(request):
    """API para listar a√±os acad√©micos"""
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
        print(f"M√©todo: {request.method}")
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
            'hours_per_week': subject.hours_per_week,
        })
    
    return JsonResponse({
        'status': 'success',
        'data': data
    })


# === APIs para gesti√≥n de Grados ===

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
            
            # Validar que el orden no est√© duplicado
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
                'message': 'Datos JSON inv√°lidos'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'})


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
            
            # Validar que el orden no est√© duplicado (excluyendo el grado actual)
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
                'message': 'Datos JSON inv√°lidos'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'})


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
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'})


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
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'})


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
            
            # Validar que el c√≥digo no est√© duplicado
            if Subject.objects.filter(code=data['code']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe una materia con c√≥digo {data["code"]}'
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
                    'message': 'Las horas por semana deben ser un n√∫mero v√°lido'
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
                'message': 'Datos JSON inv√°lidos'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'})


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
            
            # Validar que el c√≥digo no est√© duplicado (excluyendo la materia actual)
            if Subject.objects.filter(code=data['code']).exclude(id=subject_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ya existe una materia con c√≥digo {data["code"]}'
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
                    'message': 'Las horas por semana deben ser un n√∫mero v√°lido'
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
                'message': 'Datos JSON inv√°lidos'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'})


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
    
    return JsonResponse({'status': 'error', 'message': 'M√©todo no permitido'}) 
 #   A P I s   t e m p o r a l e s   p a r a   c u r s o s   -   s e   a √ ± a d i r √ ° n   a l   a r c h i v o   v i e w s . p y  
  
 #   = = =   C O U R S E S   C R U D   A P I   = = =  
  
 @ c s r f _ e x e m p t  
 d e f   c o u r s e _ l i s t _ a p i ( r e q u e s t ) :  
         " " " A P I   p a r a   l i s t a r   t o d o s   l o s   c u r s o s " " "  
         i f   r e q u e s t . m e t h o d   = =   ' G E T ' :  
                 t r y :  
                         c o u r s e s   =   C o u r s e . o b j e c t s . s e l e c t _ r e l a t e d ( ' g r a d e ' ,   ' a c a d e m i c _ y e a r ' ) . a l l ( )  
                         c o u r s e s _ d a t a   =   [ ]  
                          
                         f o r   c o u r s e   i n   c o u r s e s :  
                                 c o u r s e s _ d a t a . a p p e n d ( {  
                                         ' i d ' :   c o u r s e . i d ,  
                                         ' g r a d e _ i d ' :   c o u r s e . g r a d e . i d ,  
                                         ' g r a d e _ n a m e ' :   c o u r s e . g r a d e . n a m e ,  
                                         ' s e c t i o n ' :   c o u r s e . s e c t i o n ,  
                                         ' a c a d e m i c _ y e a r _ i d ' :   c o u r s e . a c a d e m i c _ y e a r . i d ,  
                                         ' a c a d e m i c _ y e a r _ n a m e ' :   c o u r s e . a c a d e m i c _ y e a r . n a m e ,  
                                         ' m a x _ s t u d e n t s ' :   c o u r s e . m a x _ s t u d e n t s ,  
                                         ' c u r r e n t _ s t u d e n t s _ c o u n t ' :   c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t ,  
                                         ' a v a i l a b l e _ s p o t s ' :   c o u r s e . a v a i l a b l e _ s p o t s ,  
                                         ' h o m e r o o m _ t e a c h e r ' :   c o u r s e . h o m e r o o m _ t e a c h e r . g e t _ f u l l _ n a m e ( )   i f   c o u r s e . h o m e r o o m _ t e a c h e r   e l s e   N o n e ,  
                                         ' i s _ a c t i v e ' :   c o u r s e . i s _ a c t i v e  
                                 } )  
                          
                         l o g g e r . i n f o ( f " L i s t a d o s   { l e n ( c o u r s e s _ d a t a ) }   c u r s o s " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' s u c c e s s ' ,  
                                 ' c o u r s e s ' :   c o u r s e s _ d a t a  
                         } )  
                          
                 e x c e p t   E x c e p t i o n   a s   e :  
                         l o g g e r . e r r o r ( f " E r r o r   a l   l i s t a r   c u r s o s :   { s t r ( e ) } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                 ' m e s s a g e ' :   f ' E r r o r   a l   o b t e n e r   c u r s o s :   { s t r ( e ) } '  
                         } )  
          
         r e t u r n   J s o n R e s p o n s e ( { ' s t a t u s ' :   ' e r r o r ' ,   ' m e s s a g e ' :   ' M √ © t o d o   n o   p e r m i t i d o ' } )  
  
  
 @ c s r f _ e x e m p t  
 d e f   c r e a t e _ c o u r s e _ a p i ( r e q u e s t ) :  
         " " " A P I   p a r a   c r e a r   u n   n u e v o   c u r s o " " "  
         i f   r e q u e s t . m e t h o d   = =   ' P O S T ' :  
                 t r y :  
                         d a t a   =   j s o n . l o a d s ( r e q u e s t . b o d y )  
                         g r a d e _ i d   =   d a t a . g e t ( ' g r a d e _ i d ' )  
                         s e c t i o n   =   d a t a . g e t ( ' s e c t i o n ' )  
                         a c a d e m i c _ y e a r _ i d   =   d a t a . g e t ( ' a c a d e m i c _ y e a r _ i d ' )  
                         m a x _ s t u d e n t s   =   d a t a . g e t ( ' m a x _ s t u d e n t s ' ,   3 0 )  
                          
                         #   V a l i d a c i o n e s   r e q u e r i d a s  
                         i f   n o t   a l l ( [ g r a d e _ i d ,   s e c t i o n ,   a c a d e m i c _ y e a r _ i d ] ) :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   ' G r a d o ,   s e c c i √ ≥ n   y   a √ ± o   a c a d √ © m i c o   s o n   r e q u e r i d o s '  
                                 } )  
                          
                         #   V a l i d a r   q u e   e l   g r a d o   e x i s t e  
                         t r y :  
                                 g r a d e   =   G r a d e . o b j e c t s . g e t ( i d = g r a d e _ i d )  
                         e x c e p t   G r a d e . D o e s N o t E x i s t :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   ' E l   g r a d o   e s p e c i f i c a d o   n o   e x i s t e '  
                                 } )  
                          
                         #   V a l i d a r   q u e   e l   a √ ± o   a c a d √ © m i c o   e x i s t e  
                         t r y :  
                                 a c a d e m i c _ y e a r   =   A c a d e m i c Y e a r . o b j e c t s . g e t ( i d = a c a d e m i c _ y e a r _ i d )  
                         e x c e p t   A c a d e m i c Y e a r . D o e s N o t E x i s t :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   ' E l   a √ ± o   a c a d √ © m i c o   e s p e c i f i c a d o   n o   e x i s t e '  
                                 } )  
                          
                         #   V a l i d a r   q u e   l a   s e c c i √ ≥ n   e s   v √ ° l i d a  
                         v a l i d _ s e c t i o n s   =   [ c h o i c e [ 0 ]   f o r   c h o i c e   i n   C o u r s e . S E C T I O N _ C H O I C E S ]  
                         i f   s e c t i o n   n o t   i n   v a l i d _ s e c t i o n s :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   f ' S e c c i √ ≥ n   i n v √ ° l i d a .   O p c i o n e s   v √ ° l i d a s :   { " ,   " . j o i n ( v a l i d _ s e c t i o n s ) } '  
                                 } )  
                          
                         #   V e r i f i c a r   q u e   n o   e x i s t e   y a   u n   c u r s o   c o n   l a   m i s m a   c o m b i n a c i √ ≥ n  
                         i f   C o u r s e . o b j e c t s . f i l t e r (  
                                 g r a d e = g r a d e ,    
                                 s e c t i o n = s e c t i o n ,    
                                 a c a d e m i c _ y e a r = a c a d e m i c _ y e a r  
                         ) . e x i s t s ( ) :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   f ' Y a   e x i s t e   u n   c u r s o   { g r a d e . n a m e }   -   { s e c t i o n }   p a r a   e l   a √ ± o   { a c a d e m i c _ y e a r . n a m e } '  
                                 } )  
                          
                         #   C r e a r   e l   c u r s o  
                         c o u r s e   =   C o u r s e . o b j e c t s . c r e a t e (  
                                 g r a d e = g r a d e ,  
                                 s e c t i o n = s e c t i o n ,  
                                 a c a d e m i c _ y e a r = a c a d e m i c _ y e a r ,  
                                 m a x _ s t u d e n t s = m a x _ s t u d e n t s  
                         )  
                          
                         l o g g e r . i n f o ( f " C u r s o   c r e a d o   e x i t o s a m e n t e :   { c o u r s e } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' s u c c e s s ' ,  
                                 ' m e s s a g e ' :   f ' C u r s o   { c o u r s e }   c r e a d o   e x i t o s a m e n t e ' ,  
                                 ' c o u r s e ' :   {  
                                         ' i d ' :   c o u r s e . i d ,  
                                         ' g r a d e _ n a m e ' :   c o u r s e . g r a d e . n a m e ,  
                                         ' s e c t i o n ' :   c o u r s e . s e c t i o n ,  
                                         ' a c a d e m i c _ y e a r _ n a m e ' :   c o u r s e . a c a d e m i c _ y e a r . n a m e ,  
                                         ' m a x _ s t u d e n t s ' :   c o u r s e . m a x _ s t u d e n t s ,  
                                         ' c u r r e n t _ s t u d e n t s _ c o u n t ' :   c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t ,  
                                         ' a v a i l a b l e _ s p o t s ' :   c o u r s e . a v a i l a b l e _ s p o t s ,  
                                         ' i s _ a c t i v e ' :   c o u r s e . i s _ a c t i v e  
                                 }  
                         } )  
                          
                 e x c e p t   j s o n . J S O N D e c o d e E r r o r :  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                 ' m e s s a g e ' :   ' D a t o s   J S O N   i n v √ ° l i d o s '  
                         } )  
                 e x c e p t   E x c e p t i o n   a s   e :  
                         l o g g e r . e r r o r ( f " E r r o r   a l   c r e a r   c u r s o :   { s t r ( e ) } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                 ' m e s s a g e ' :   f ' E r r o r   i n t e r n o :   { s t r ( e ) } '  
                         } )  
          
         r e t u r n   J s o n R e s p o n s e ( { ' s t a t u s ' :   ' e r r o r ' ,   ' m e s s a g e ' :   ' M √ © t o d o   n o   p e r m i t i d o ' } )  
  
  
 @ c s r f _ e x e m p t  
 d e f   u p d a t e _ c o u r s e _ a p i ( r e q u e s t ,   c o u r s e _ i d ) :  
         " " " A P I   p a r a   a c t u a l i z a r   u n   c u r s o   e x i s t e n t e " " "  
         i f   r e q u e s t . m e t h o d   = =   ' P U T ' :  
                 t r y :  
                         d a t a   =   j s o n . l o a d s ( r e q u e s t . b o d y )  
                          
                         t r y :  
                                 c o u r s e   =   C o u r s e . o b j e c t s . s e l e c t _ r e l a t e d ( ' g r a d e ' ,   ' a c a d e m i c _ y e a r ' ) . g e t ( i d = c o u r s e _ i d )  
                         e x c e p t   C o u r s e . D o e s N o t E x i s t :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   ' C u r s o   n o   e n c o n t r a d o '  
                                 } )  
                          
                         #   A c t u a l i z a r   c a m p o s   s i   s e   p r o p o r c i o n a n  
                         g r a d e _ i d   =   d a t a . g e t ( ' g r a d e _ i d ' )  
                         s e c t i o n   =   d a t a . g e t ( ' s e c t i o n ' )  
                         a c a d e m i c _ y e a r _ i d   =   d a t a . g e t ( ' a c a d e m i c _ y e a r _ i d ' )  
                         m a x _ s t u d e n t s   =   d a t a . g e t ( ' m a x _ s t u d e n t s ' )  
                         i s _ a c t i v e   =   d a t a . g e t ( ' i s _ a c t i v e ' )  
                          
                         #   V a l i d a r   g r a d o   s i   s e   p r o p o r c i o n a  
                         i f   g r a d e _ i d   i s   n o t   N o n e :  
                                 t r y :  
                                         g r a d e   =   G r a d e . o b j e c t s . g e t ( i d = g r a d e _ i d )  
                                         c o u r s e . g r a d e   =   g r a d e  
                                 e x c e p t   G r a d e . D o e s N o t E x i s t :  
                                         r e t u r n   J s o n R e s p o n s e ( {  
                                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                                 ' m e s s a g e ' :   ' E l   g r a d o   e s p e c i f i c a d o   n o   e x i s t e '  
                                         } )  
                          
                         #   V a l i d a r   a √ ± o   a c a d √ © m i c o   s i   s e   p r o p o r c i o n a  
                         i f   a c a d e m i c _ y e a r _ i d   i s   n o t   N o n e :  
                                 t r y :  
                                         a c a d e m i c _ y e a r   =   A c a d e m i c Y e a r . o b j e c t s . g e t ( i d = a c a d e m i c _ y e a r _ i d )  
                                         c o u r s e . a c a d e m i c _ y e a r   =   a c a d e m i c _ y e a r  
                                 e x c e p t   A c a d e m i c Y e a r . D o e s N o t E x i s t :  
                                         r e t u r n   J s o n R e s p o n s e ( {  
                                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                                 ' m e s s a g e ' :   ' E l   a √ ± o   a c a d √ © m i c o   e s p e c i f i c a d o   n o   e x i s t e '  
                                         } )  
                          
                         #   V a l i d a r   s e c c i √ ≥ n   s i   s e   p r o p o r c i o n a  
                         i f   s e c t i o n   i s   n o t   N o n e :  
                                 v a l i d _ s e c t i o n s   =   [ c h o i c e [ 0 ]   f o r   c h o i c e   i n   C o u r s e . S E C T I O N _ C H O I C E S ]  
                                 i f   s e c t i o n   n o t   i n   v a l i d _ s e c t i o n s :  
                                         r e t u r n   J s o n R e s p o n s e ( {  
                                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                                 ' m e s s a g e ' :   f ' S e c c i √ ≥ n   i n v √ ° l i d a .   O p c i o n e s   v √ ° l i d a s :   { " ,   " . j o i n ( v a l i d _ s e c t i o n s ) } '  
                                         } )  
                                 c o u r s e . s e c t i o n   =   s e c t i o n  
                          
                         #   V a l i d a r   n √ ∫ m e r o   m √ ° x i m o   d e   e s t u d i a n t e s  
                         i f   m a x _ s t u d e n t s   i s   n o t   N o n e :  
                                 i f   m a x _ s t u d e n t s   <   c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t :  
                                         r e t u r n   J s o n R e s p o n s e ( {  
                                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                                 ' m e s s a g e ' :   f ' N o   s e   p u e d e   r e d u c i r   e l   m √ ° x i m o   a   { m a x _ s t u d e n t s } .   E s t u d i a n t e s   a c t u a l e s :   { c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t } '  
                                         } )  
                                 c o u r s e . m a x _ s t u d e n t s   =   m a x _ s t u d e n t s  
                          
                         #   A c t u a l i z a r   e s t a d o   a c t i v o   s i   s e   p r o p o r c i o n a  
                         i f   i s _ a c t i v e   i s   n o t   N o n e :  
                                 c o u r s e . i s _ a c t i v e   =   i s _ a c t i v e  
                          
                         #   V e r i f i c a r   u n i c i d a d   a n t e s   d e   g u a r d a r   ( s i   s e   m o d i f i c a r o n   c a m p o s   c l a v e )  
                         i f   a n y ( [ g r a d e _ i d   i s   n o t   N o n e ,   s e c t i o n   i s   n o t   N o n e ,   a c a d e m i c _ y e a r _ i d   i s   n o t   N o n e ] ) :  
                                 e x i s t i n g _ c o u r s e   =   C o u r s e . o b j e c t s . f i l t e r (  
                                         g r a d e = c o u r s e . g r a d e ,  
                                         s e c t i o n = c o u r s e . s e c t i o n ,  
                                         a c a d e m i c _ y e a r = c o u r s e . a c a d e m i c _ y e a r  
                                 ) . e x c l u d e ( i d = c o u r s e . i d )  
                                  
                                 i f   e x i s t i n g _ c o u r s e . e x i s t s ( ) :  
                                         r e t u r n   J s o n R e s p o n s e ( {  
                                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                                 ' m e s s a g e ' :   f ' Y a   e x i s t e   u n   c u r s o   { c o u r s e . g r a d e . n a m e }   -   { c o u r s e . s e c t i o n }   p a r a   e l   a √ ± o   { c o u r s e . a c a d e m i c _ y e a r . n a m e } '  
                                         } )  
                          
                         c o u r s e . s a v e ( )  
                          
                         l o g g e r . i n f o ( f " C u r s o   a c t u a l i z a d o   e x i t o s a m e n t e :   { c o u r s e } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' s u c c e s s ' ,  
                                 ' m e s s a g e ' :   f ' C u r s o   { c o u r s e }   a c t u a l i z a d o   e x i t o s a m e n t e ' ,  
                                 ' c o u r s e ' :   {  
                                         ' i d ' :   c o u r s e . i d ,  
                                         ' g r a d e _ n a m e ' :   c o u r s e . g r a d e . n a m e ,  
                                         ' s e c t i o n ' :   c o u r s e . s e c t i o n ,  
                                         ' a c a d e m i c _ y e a r _ n a m e ' :   c o u r s e . a c a d e m i c _ y e a r . n a m e ,  
                                         ' m a x _ s t u d e n t s ' :   c o u r s e . m a x _ s t u d e n t s ,  
                                         ' c u r r e n t _ s t u d e n t s _ c o u n t ' :   c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t ,  
                                         ' a v a i l a b l e _ s p o t s ' :   c o u r s e . a v a i l a b l e _ s p o t s ,  
                                         ' i s _ a c t i v e ' :   c o u r s e . i s _ a c t i v e  
                                 }  
                         } )  
                          
                 e x c e p t   j s o n . J S O N D e c o d e E r r o r :  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                 ' m e s s a g e ' :   ' D a t o s   J S O N   i n v √ ° l i d o s '  
                         } )  
                 e x c e p t   E x c e p t i o n   a s   e :  
                         l o g g e r . e r r o r ( f " E r r o r   a l   a c t u a l i z a r   c u r s o :   { s t r ( e ) } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                 ' m e s s a g e ' :   f ' E r r o r   i n t e r n o :   { s t r ( e ) } '  
                         } )  
          
         r e t u r n   J s o n R e s p o n s e ( { ' s t a t u s ' :   ' e r r o r ' ,   ' m e s s a g e ' :   ' M √ © t o d o   n o   p e r m i t i d o ' } )  
  
  
 @ c s r f _ e x e m p t  
 d e f   d e l e t e _ c o u r s e _ a p i ( r e q u e s t ,   c o u r s e _ i d ) :  
         " " " A P I   p a r a   e l i m i n a r   u n   c u r s o " " "  
         i f   r e q u e s t . m e t h o d   = =   ' D E L E T E ' :  
                 t r y :  
                         t r y :  
                                 c o u r s e   =   C o u r s e . o b j e c t s . g e t ( i d = c o u r s e _ i d )  
                         e x c e p t   C o u r s e . D o e s N o t E x i s t :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   ' C u r s o   n o   e n c o n t r a d o '  
                                 } )  
                          
                         #   V e r i f i c a r   s i   t i e n e   e s t u d i a n t e s   a s i g n a d o s  
                         i f   c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t   >   0 :  
                                 r e t u r n   J s o n R e s p o n s e ( {  
                                         ' s t a t u s ' :   ' e r r o r ' ,  
                                         ' m e s s a g e ' :   f ' N o   s e   p u e d e   e l i m i n a r   e l   c u r s o .   T i e n e   { c o u r s e . c u r r e n t _ s t u d e n t s _ c o u n t }   e s t u d i a n t e ( s )   a s i g n a d o ( s ) '  
                                 } )  
                          
                         c o u r s e _ i n f o   =   s t r ( c o u r s e )  
                         c o u r s e . d e l e t e ( )  
                          
                         l o g g e r . i n f o ( f " C u r s o   e l i m i n a d o   e x i t o s a m e n t e :   { c o u r s e _ i n f o } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' s u c c e s s ' ,  
                                 ' m e s s a g e ' :   f ' C u r s o   { c o u r s e _ i n f o }   e l i m i n a d o   e x i t o s a m e n t e '  
                         } )  
                          
                 e x c e p t   E x c e p t i o n   a s   e :  
                         l o g g e r . e r r o r ( f " E r r o r   a l   e l i m i n a r   c u r s o :   { s t r ( e ) } " )  
                         r e t u r n   J s o n R e s p o n s e ( {  
                                 ' s t a t u s ' :   ' e r r o r ' ,  
                                 ' m e s s a g e ' :   f ' E r r o r   i n t e r n o :   { s t r ( e ) } '  
                         } )  
          
         r e t u r n   J s o n R e s p o n s e ( { ' s t a t u s ' :   ' e r r o r ' ,   ' m e s s a g e ' :   ' M √ © t o d o   n o   p e r m i t i d o ' } )  
 