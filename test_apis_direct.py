#!/usr/bin/env python
"""
Script para probar las APIs del sistema de horarios directamente
"""

import requests
import json

def test_resources_api():
    """Probar la API de recursos"""
    print("🧪 PROBANDO API DE RECURSOS")
    print("=" * 50)
    
    try:
        url = "http://127.0.0.1:8000/academic-system/schedules/resources/"
        response = requests.get(url)
        
        print(f"📡 Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ API funcionando correctamente")
                print(f"📊 Estructura de respuesta: {data.get('status')}")
                
                if data.get('status') == 'success':
                    api_data = data.get('data', {})
                    print(f"\n📊 DATOS DISPONIBLES:")
                    print(f"   • Cursos: {len(api_data.get('courses', []))}")
                    print(f"   • Profesores: {len(api_data.get('teachers', []))}")
                    print(f"   • Salones: {len(api_data.get('classrooms', []))}")
                    print(f"   • Materias: {len(api_data.get('subjects', []))}")
                    print(f"   • Franjas: {len(api_data.get('time_slots', []))}")
                    
                    # Mostrar ejemplos
                    if api_data.get('courses'):
                        print(f"\n📚 EJEMPLOS DE CURSOS:")
                        for course in api_data['courses'][:3]:
                            print(f"   • ID: {course['id']}, Nombre: {course['name']}")
                    
                    if api_data.get('teachers'):
                        print(f"\n👨‍🏫 EJEMPLOS DE PROFESORES:")
                        for teacher in api_data['teachers'][:3]:
                            print(f"   • ID: {teacher['id']}, Nombre: {teacher['name']}")
                    
                    # Verificar si hay datos suficientes
                    all_counts = [
                        len(api_data.get('courses', [])),
                        len(api_data.get('teachers', [])),
                        len(api_data.get('classrooms', [])),
                        len(api_data.get('subjects', [])),
                        len(api_data.get('time_slots', []))
                    ]
                    
                    if all(count > 0 for count in all_counts):
                        print(f"\n✅ TODOS LOS DATOS DISPONIBLES - DROPDOWNS DEBERÍAN FUNCIONAR")
                        return True
                    else:
                        empty_fields = []
                        if not api_data.get('courses'): empty_fields.append('cursos')
                        if not api_data.get('teachers'): empty_fields.append('profesores')
                        if not api_data.get('classrooms'): empty_fields.append('salones')
                        if not api_data.get('subjects'): empty_fields.append('materias')
                        if not api_data.get('time_slots'): empty_fields.append('franjas')
                        
                        print(f"\n❌ FALTAN DATOS EN: {', '.join(empty_fields)}")
                        return False
                        
                else:
                    print(f"❌ Error en API: {data.get('message')}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"❌ Error: Respuesta no es JSON válido")
                print(f"Contenido: {response.text[:200]}")
                return False
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Contenido: {response.text[:200]}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_schedule_list_api():
    """Probar la API de lista de horarios"""
    print(f"\n🧪 PROBANDO API DE LISTA DE HORARIOS")
    print("=" * 50)
    
    try:
        url = "http://127.0.0.1:8000/academic-system/schedules/api/"
        response = requests.get(url)
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                schedules = data.get('data', [])
                print(f"✅ API funcionando - {len(schedules)} horarios encontrados")
                
                if schedules:
                    print(f"\n📅 EJEMPLO DE HORARIO:")
                    example = schedules[0]
                    print(f"   • Curso: {example.get('course_name')}")
                    print(f"   • Materia: {example.get('subject_name')}")
                    print(f"   • Profesor: {example.get('teacher_name')}")
                    print(f"   • Día: {example.get('weekday')}")
                    print(f"   • Hora: {example.get('time_slot_name')}")
                
                return True
            else:
                print(f"❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN DE APIs DEL SISTEMA DE HORARIOS")
    print("=" * 60)
    
    # Probar API de recursos
    resources_ok = test_resources_api()
    
    # Probar API de horarios
    schedules_ok = test_schedule_list_api()
    
    print(f"\n📋 RESUMEN:")
    print("=" * 30)
    print(f"🔗 API de Recursos: {'✅ OK' if resources_ok else '❌ FALLA'}")
    print(f"📅 API de Horarios: {'✅ OK' if schedules_ok else '❌ FALLA'}")
    
    if resources_ok and schedules_ok:
        print(f"\n🎉 ¡APIS FUNCIONANDO CORRECTAMENTE!")
        print(f"💡 Los dropdowns en el frontend deberían llenarse ahora")
        print(f"🌐 Ve a: http://127.0.0.1:8000/academic-system/schedules/")
        print(f"📝 Haz clic en 'Crear Nuevo Horario' para verificar los dropdowns")
    else:
        print(f"\n⚠️ Hay problemas con las APIs")
        
    print(f"\n🔧 ACCIONES RECOMENDADAS:")
    print(f"1. Ve a la página: http://127.0.0.1:8000/academic-system/schedules/")
    print(f"2. Abre las herramientas de desarrollador (F12)")
    print(f"3. Ve a la pestaña Console")
    print(f"4. Haz clic en 'Crear Nuevo Horario'")
    print(f"5. Revisa si hay errores en la consola")

if __name__ == "__main__":
    main()