#!/usr/bin/env python3
"""
Script para probar las APIs de cursos del sistema académico

Este script verifica que todas las APIs CRUD de cursos funcionen correctamente.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8001"
COURSES_API_BASE = f"{BASE_URL}/academics_extended/api/courses"

def print_header(title):
    """Imprime un encabezado decorado"""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {message}")

def test_list_courses():
    """Prueba la API para listar cursos"""
    print_header("PRUEBA: Listar Cursos")
    
    try:
        response = requests.get(f"{COURSES_API_BASE}/")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                courses = data.get('courses', [])
                print_success(f"API funciona correctamente")
                print_info(f"Cursos encontrados: {len(courses)}")
                
                if courses:
                    print(f"\n📋 Primeros 3 cursos:")
                    for i, course in enumerate(courses[:3]):
                        print(f"   {i+1}. {course['grade_name']} - {course['section']} ({course['academic_year_name']})")
                        print(f"      Estudiantes: {course['current_students_count']}/{course['max_students']}")
                        print(f"      Activo: {'Sí' if course['is_active'] else 'No'}")
                
                return True, courses
            else:
                print_error(f"Error en respuesta: {data.get('message', 'Sin mensaje')}")
                return False, []
        else:
            print_error(f"Error HTTP: {response.status_code}")
            return False, []
            
    except Exception as e:
        print_error(f"Error de conexión: {str(e)}")
        return False, []

def test_get_grades_and_years():
    """Obtiene grados y años académicos disponibles para las pruebas"""
    print_header("OBTENER DATOS DE REFERENCIA")
    
    try:
        # Obtener grados
        grades_response = requests.get(f"{BASE_URL}/academics_extended/api/grades/")
        grades = []
        if grades_response.status_code == 200:
            grades_data = grades_response.json()
            if grades_data.get('status') == 'success':
                grades = grades_data.get('grades', [])
                print_success(f"Grados disponibles: {len(grades)}")
        
        # Obtener años académicos
        years_response = requests.get(f"{BASE_URL}/academics_extended/api/academic-years/")
        years = []
        if years_response.status_code == 200:
            years_data = years_response.json()
            if years_data.get('status') == 'success':
                years = years_data.get('academic_years', [])
                print_success(f"Años académicos disponibles: {len(years)}")
        
        return grades, years
        
    except Exception as e:
        print_error(f"Error obteniendo datos de referencia: {str(e)}")
        return [], []

def test_create_course(grades, years):
    """Prueba la API para crear un nuevo curso"""
    print_header("PRUEBA: Crear Nuevo Curso")
    
    if not grades or not years:
        print_error("No hay datos de referencia disponibles")
        return False, None
    
    # Buscar un grado y año académico
    test_grade = grades[0]  # Primer grado
    test_year = years[0]   # Primer año académico
    
    # Datos del curso de prueba
    course_data = {
        "grade_id": test_grade['id'],
        "section": "TEST",  # Sección especial para pruebas
        "academic_year_id": test_year['id'],
        "max_students": 20,
        "is_active": True
    }
    
    try:
        response = requests.post(
            f"{COURSES_API_BASE}/create/",
            json=course_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                course = data.get('course')
                print_success("Curso creado exitosamente")
                print_info(f"ID: {course['id']}")
                print_info(f"Curso: {course['grade_name']} - {course['section']}")
                print_info(f"Año: {course['academic_year_name']}")
                print_info(f"Capacidad: {course['max_students']}")
                return True, course
            else:
                print_error(f"Error en creación: {data.get('message', 'Sin mensaje')}")
                return False, None
        else:
            print_error(f"Error HTTP: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error de conexión: {str(e)}")
        return False, None

def test_update_course(course):
    """Prueba la API para actualizar un curso"""
    print_header("PRUEBA: Actualizar Curso")
    
    if not course:
        print_error("No hay curso para actualizar")
        return False
    
    # Datos para actualizar
    update_data = {
        "max_students": 25,  # Aumentar capacidad
        "is_active": True
    }
    
    try:
        response = requests.put(
            f"{COURSES_API_BASE}/{course['id']}/update/",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                updated_course = data.get('course')
                print_success("Curso actualizado exitosamente")
                print_info(f"Nueva capacidad: {updated_course['max_students']}")
                return True
            else:
                print_error(f"Error en actualización: {data.get('message', 'Sin mensaje')}")
                return False
        else:
            print_error(f"Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error de conexión: {str(e)}")
        return False

def test_delete_course(course):
    """Prueba la API para eliminar un curso"""
    print_header("PRUEBA: Eliminar Curso")
    
    if not course:
        print_error("No hay curso para eliminar")
        return False
    
    try:
        response = requests.delete(f"{COURSES_API_BASE}/{course['id']}/delete/")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                print_success("Curso eliminado exitosamente")
                print_info(f"Curso eliminado: {course['grade_name']} - {course['section']}")
                return True
            else:
                print_error(f"Error en eliminación: {data.get('message', 'Sin mensaje')}")
                return False
        else:
            print_error(f"Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error de conexión: {str(e)}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print_header("INICIANDO PRUEBAS DE APIs DE CURSOS")
    
    results = {
        'list': False,
        'create': False,
        'update': False,
        'delete': False
    }
    
    # 1. Probar listado de cursos
    list_success, existing_courses = test_list_courses()
    results['list'] = list_success
    
    if not list_success:
        print_error("Falla en listado - Cancelando pruebas")
        return results
    
    # 2. Obtener datos de referencia
    grades, years = test_get_grades_and_years()
    
    if not grades or not years:
        print_error("No hay datos de referencia - Cancelando pruebas de creación")
        return results
    
    # 3. Probar creación de curso
    create_success, test_course = test_create_course(grades, years)
    results['create'] = create_success
    
    if create_success and test_course:
        # 4. Probar actualización
        update_success = test_update_course(test_course)
        results['update'] = update_success
        
        # 5. Probar eliminación
        delete_success = test_delete_course(test_course)
        results['delete'] = delete_success
    
    return results

def print_final_report(results):
    """Imprime el reporte final"""
    print_header("REPORTE FINAL DE PRUEBAS")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"📊 Resultados:")
    print(f"   • Listar cursos: {'✅ PASS' if results['list'] else '❌ FAIL'}")
    print(f"   • Crear curso: {'✅ PASS' if results['create'] else '❌ FAIL'}")
    print(f"   • Actualizar curso: {'✅ PASS' if results['update'] else '❌ FAIL'}")
    print(f"   • Eliminar curso: {'✅ PASS' if results['delete'] else '❌ FAIL'}")
    
    print(f"\n🎯 Resumen: {passed_tests}/{total_tests} pruebas exitosas")
    
    if passed_tests == total_tests:
        print_success("¡Todas las APIs de cursos funcionan correctamente! 🎉")
    else:
        print_error(f"Se encontraron {total_tests - passed_tests} fallas en las APIs")
    
    return passed_tests == total_tests

if __name__ == '__main__':
    print("🏫 PROBADOR DE APIs DE CURSOS")
    print("Asegúrese de que el servidor de Django esté ejecutándose en http://127.0.0.1:8001")
    
    try:
        # Verificar que el servidor esté disponible
        response = requests.get(BASE_URL, timeout=5)
        print_success("Servidor Django disponible")
    except:
        print_error("Servidor Django no disponible - Verifique que esté ejecutándose")
        sys.exit(1)
    
    # Ejecutar todas las pruebas
    results = run_all_tests()
    
    # Reporte final
    all_passed = print_final_report(results)
    
    # Código de salida
    sys.exit(0 if all_passed else 1)