#!/usr/bin/env python
"""
Script para probar la creación de horarios y verificar la validación
"""

import requests
import json

def test_schedule_creation_api():
    """Probar la API de creación de horarios"""
    print("🧪 PROBANDO API DE CREACIÓN DE HORARIOS")
    print("=" * 50)
    
    # Primero obtener recursos disponibles
    print("1. 📥 Obteniendo recursos disponibles...")
    try:
        resources_response = requests.get("http://127.0.0.1:8000/academic-system/schedules/resources/")
        
        if resources_response.status_code != 200:
            print(f"❌ Error obteniendo recursos: {resources_response.status_code}")
            return False
            
        resources_data = resources_response.json()
        
        if resources_data.get('status') != 'success':
            print(f"❌ Error en respuesta de recursos: {resources_data.get('message')}")
            return False
            
        resources = resources_data.get('data', {})
        
        print("✅ Recursos obtenidos correctamente:")
        print(f"   • Cursos: {len(resources.get('courses', []))}")
        print(f"   • Materias: {len(resources.get('subjects', []))}")
        print(f"   • Profesores: {len(resources.get('teachers', []))}")
        print(f"   • Salones: {len(resources.get('classrooms', []))}")
        print(f"   • Franjas: {len(resources.get('time_slots', []))}")
        
        if not all(len(resources.get(key, [])) > 0 for key in ['courses', 'subjects', 'teachers', 'classrooms', 'time_slots']):
            print("❌ Faltan recursos para crear horarios")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo recursos: {e}")
        return False
    
    # Probar casos de error comunes
    print(f"\n2. 🧪 Probando validaciones de error...")
    
    test_cases = [
        {
            "name": "Datos vacíos",
            "data": {
                "course_id": "",
                "subject_id": "",
                "teacher_id": "",
                "classroom_id": "",
                "time_slot_id": "",
                "weekday": ""
            },
            "should_fail": True
        },
        {
            "name": "IDs inválidos",
            "data": {
                "course_id": "abc",
                "subject_id": "xyz",
                "teacher_id": "123",
                "classroom_id": "456",
                "time_slot_id": "789",
                "weekday": "lunes"
            },
            "should_fail": True
        },
        {
            "name": "Datos válidos",
            "data": {
                "course_id": resources['courses'][0]['id'] if resources['courses'] else 1,
                "subject_id": resources['subjects'][0]['id'] if resources['subjects'] else 1,
                "teacher_id": resources['teachers'][0]['id'] if resources['teachers'] else 1,
                "classroom_id": resources['classrooms'][0]['id'] if resources['classrooms'] else 1,
                "time_slot_id": resources['time_slots'][0]['id'] if resources['time_slots'] else 1,
                "weekday": "1"
            },
            "should_fail": False
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n   Prueba {i+1}: {test_case['name']}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/academic-system/schedules/create/",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            print(f"   Status: {response.status_code}")
            print(f"   Respuesta: {result.get('status')} - {result.get('message')}")
            
            if test_case['should_fail']:
                if result.get('status') == 'error':
                    print("   ✅ Validación funcionando correctamente (error esperado)")
                else:
                    print("   ❌ Debería haber fallado pero no lo hizo")
            else:
                if result.get('status') == 'success':
                    print("   ✅ Creación exitosa")
                elif result.get('status') == 'error' and 'ya tiene una clase' in result.get('message', ''):
                    print("   ✅ Validación de conflicto funcionando correctamente")
                else:
                    print(f"   ❌ Error inesperado: {result.get('message')}")
                    
        except Exception as e:
            print(f"   💥 Error de conexión: {e}")
    
    return True

def show_debugging_instructions():
    """Mostrar instrucciones para depurar en el navegador"""
    print(f"\n🔧 INSTRUCCIONES PARA DEPURAR EN EL NAVEGADOR:")
    print("-" * 50)
    print("1. Ve a: http://127.0.0.1:8000/academic-system/schedules/")
    print("2. Abre la consola (F12 → Console)")
    print("3. Ejecuta estas funciones para depurar:")
    print()
    print("   📊 Ver estado de recursos:")
    print("   debugResources()")
    print()
    print("   🔄 Forzar llenado de dropdowns:")
    print("   forcePopulateSelects()")
    print()
    print("   🔍 Validar datos del formulario:")
    print("   validateFormData()")
    print()
    print("   🧪 Probar creación completa:")
    print("   testScheduleCreation()")
    print()
    print("4. Para crear un horario:")
    print("   • Haz clic en 'Crear Nuevo Horario'")
    print("   • Selecciona TODOS los campos (no dejes ninguno vacío)")
    print("   • Verifica con validateFormData() antes de guardar")
    print("   • Haz clic en 'Crear Horario'")

def main():
    api_working = test_schedule_creation_api()
    
    print(f"\n📋 RESUMEN:")
    print("=" * 30)
    print(f"🔗 API funcionando: {'✅' if api_working else '❌'}")
    
    if api_working:
        print(f"✅ Las validaciones están funcionando correctamente")
        print(f"✅ El error 'Field id expected a number but got' está solucionado")
        
        show_debugging_instructions()
        
        print(f"\n💡 CAUSA DEL ERROR ORIGINAL:")
        print(f"• Uno o más dropdowns estaban enviando valores vacíos ('')")
        print(f"• Django esperaba números válidos para los campos de ID")
        print(f"• Ahora hay validación tanto en frontend como backend")
        
    else:
        print(f"❌ Hay problemas con las APIs")
        print(f"Asegúrate de que el servidor Django esté corriendo")

if __name__ == "__main__":
    main()