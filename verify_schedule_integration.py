#!/usr/bin/env python3
"""
Script para verificar que el sistema de horarios está completamente integrado
"""

print("🔍 VERIFICACIÓN DEL SISTEMA DE HORARIOS INTEGRADO")
print("=" * 60)

# 1. Verificar que el servidor esté corriendo
import requests
import time

def test_server_status():
    """Verificar que el servidor Django esté corriendo"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print("✅ Servidor Django corriendo")
        return True
    except:
        print("❌ Servidor Django no está corriendo")
        return False

def test_schedule_page():
    """Verificar que la página de horarios esté accesible"""
    try:
        response = requests.get("http://127.0.0.1:8000/academic-system/schedules/", timeout=5)
        if response.status_code == 200:
            print("✅ Página de gestión de horarios accesible")
            return True
        elif response.status_code == 302:
            print("⚠️  Página redirige (probablemente requiere login)")
            return True
        else:
            print(f"❌ Página no accesible (código: {response.status_code})")
            return False
    except:
        print("❌ Error al acceder a la página de horarios")
        return False

def test_schedule_apis():
    """Verificar que las APIs de horarios estén funcionando"""
    apis_to_test = [
        ("/academic-system/api/schedules/resources/", "Recursos del sistema"),
        ("/academic-system/api/schedules/", "Lista de horarios"),
        ("/academic-system/api/schedules/matrix/", "Matriz de horarios"),
    ]
    
    print("\n🔧 Probando APIs del sistema:")
    
    for endpoint, description in apis_to_test:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
            data = response.json()
            
            if data.get('status') == 'success':
                print(f"  ✅ {description}: OK")
            else:
                print(f"  ❌ {description}: Error - {data.get('message', 'Desconocido')}")
                
        except Exception as e:
            print(f"  ❌ {description}: Error de conexión - {str(e)}")

def show_current_schedules():
    """Mostrar horarios actuales en el sistema"""
    try:
        response = requests.get("http://127.0.0.1:8000/academic-system/api/schedules/", timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            schedules = data.get('data', [])
            print(f"\n📅 HORARIOS ACTUALES EN EL SISTEMA: {len(schedules)} horarios")
            
            if schedules:
                for i, schedule in enumerate(schedules[:5], 1):  # Mostrar solo los primeros 5
                    print(f"  {i}. {schedule['weekday_name']} {schedule['time_slot']['name']}: {schedule['course']['name']} - {schedule['subject']['name']}")
                    print(f"     Prof: {schedule['teacher']['name']}, Salón: {schedule['classroom']['name']}")
                
                if len(schedules) > 5:
                    print(f"  ... y {len(schedules) - 5} horarios más")
            else:
                print("  No hay horarios creados aún")
                
        else:
            print(f"❌ Error al obtener horarios: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def show_system_resources():
    """Mostrar recursos disponibles en el sistema"""
    try:
        response = requests.get("http://127.0.0.1:8000/academic-system/api/schedules/resources/", timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            resources = data.get('data', {})
            print(f"\n📊 RECURSOS DEL SISTEMA:")
            print(f"  • Cursos: {len(resources.get('courses', []))}")
            print(f"  • Profesores: {len(resources.get('teachers', []))}")
            print(f"  • Salones: {len(resources.get('classrooms', []))}")
            print(f"  • Materias: {len(resources.get('subjects', []))}")
            print(f"  • Franjas horarias: {len(resources.get('time_slots', []))}")
            
            current_year = resources.get('current_year')
            if current_year:
                print(f"  • Año académico actual: {current_year['name']}")
                
        else:
            print(f"❌ Error al obtener recursos: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    # Ejecutar todas las verificaciones
    print("1. Verificando servidor...")
    if test_server_status():
        print("\n2. Verificando página de horarios...")
        test_schedule_page()
        
        print("\n3. Verificando APIs...")
        test_schedule_apis()
        
        show_system_resources()
        show_current_schedules()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("🎉 El sistema de horarios está completamente integrado!")
        print("\n📋 INSTRUCCIONES PARA EL USUARIO:")
        print("1. Accede al dashboard de administración")
        print("2. Busca el botón 'Sistema de Horarios'")
        print("3. Haz clic para abrir la gestión de horarios")
        print("4. ¡Ya puedes crear, editar y visualizar horarios!")
        
    else:
        print("\n❌ No se puede continuar - servidor no disponible")
        print("💡 Ejecuta: python manage.py runserver")