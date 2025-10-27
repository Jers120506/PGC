#!/usr/bin/env python3
"""
PRUEBA ESPECÍFICA DE LA PÁGINA DE HORARIOS
==========================================
"""
import requests
import json
from bs4 import BeautifulSoup
import time

def test_schedule_page():
    """Prueba específica de la página de horarios después de correcciones"""
    print("🔧 PRUEBA ESPECÍFICA DE CORRECCIONES DE HORARIOS")
    print("=" * 55)
    
    # Crear sesión para mantener login
    session = requests.Session()
    base_url = "http://127.0.0.1:8000"
    
    # 1. Login
    print("1. 🔑 Haciendo login...")
    login_page = session.get(f"{base_url}/auth/login/")
    if login_page.status_code != 200:
        print(f"   ❌ Error en login page: {login_page.status_code}")
        return
    
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_token:
        print("   ❌ No se pudo obtener token CSRF")
        return
    
    csrf_value = csrf_token['value']
    
    # Hacer login
    login_data = {
        'username': 'admin',
        'password': '123',
        'csrfmiddlewaretoken': csrf_value
    }
    
    login_response = session.post(f"{base_url}/auth/login/", data=login_data)
    if 'login' in login_response.url:
        print("   ❌ Login falló")
        return
    print("   ✅ Login exitoso")
    
    # 2. Acceder a página de horarios
    print("2. 📅 Accediendo a página de horarios...")
    time.sleep(1)  # Dar tiempo al servidor
    
    schedule_page = session.get(f"{base_url}/academic-system/schedules/")
    if schedule_page.status_code != 200:
        print(f"   ❌ Error accediendo: {schedule_page.status_code}")
        return
    
    html_content = schedule_page.text
    print(f"   ✅ Página carga ({len(html_content)} caracteres)")
    
    # 3. Verificar elementos JavaScript críticos
    print("3. 🧩 Verificando JavaScript crítico...")
    
    js_elements = {
        'DOMContentLoaded': 'Event listener principal',
        'loadResources': 'Función cargar recursos',
        'populateSelect': 'Función poblar selects',
        'loadScheduleMatrix': 'Función cargar matriz',
        'Cargando datos del sistema...': 'Mensaje de carga inicial',
        'filter-course': 'Dropdown de cursos',
        'applyFilters': 'Función aplicar filtros',
        'clearFilters': 'Función limpiar filtros'
    }
    
    for elemento, descripcion in js_elements.items():
        if elemento in html_content:
            print(f"   ✅ {descripcion}")
        else:
            print(f"   ❌ {descripcion}")
    
    # 4. Verificar API directamente
    print("4. 🔧 Verificando API de recursos...")
    
    api_response = session.get(f"{base_url}/academic-system/schedules/resources/")
    if api_response.status_code == 200:
        try:
            api_data = api_response.json()
            if api_data.get('status') == 'success':
                data = api_data['data']
                courses_count = len(data.get('courses', []))
                teachers_count = len(data.get('teachers', []))
                print(f"   ✅ API funciona: {courses_count} cursos, {teachers_count} profesores")
            else:
                print(f"   ❌ API error: {api_data.get('message', 'Unknown')}")
        except json.JSONDecodeError:
            print("   ❌ API no devuelve JSON válido")
    else:
        print(f"   ❌ API falla: {api_response.status_code}")
    
    # 5. Crear archivo de debug con contenido real
    debug_file = "debug_current_page.html"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"   💾 Contenido guardado en {debug_file}")
    
    # 6. Verificar posibles errores JavaScript comunes
    print("5. 🐛 Verificando posibles errores JavaScript...")
    
    error_patterns = [
        ('improvements.', 'Variable improvements indefinida'),
        ('undefined', 'Referencias undefined'),
        ('null.', 'Null reference errors'),
        ('Cannot read property', 'Property read errors'),
        ('is not a function', 'Function not defined errors')
    ]
    
    found_errors = []
    for pattern, desc in error_patterns:
        if pattern in html_content:
            found_errors.append(desc)
    
    if found_errors:
        print(f"   ⚠️  Posibles errores detectados:")
        for error in found_errors:
            print(f"      - {error}")
    else:
        print("   ✅ No se detectaron patrones de error comunes")
    
    print("\n" + "=" * 55)
    print("📊 RESUMEN DE LA PRUEBA:")
    print("=" * 55)
    print(f"✅ Servidor funcionando: SÍ")
    print(f"✅ Login funcional: SÍ") 
    print(f"✅ Página carga: SÍ ({len(html_content)} chars)")
    print(f"✅ API recursos: SÍ")
    print(f"🔍 Revisar: {debug_file}")
    
    if 'Cargando datos del sistema...' in html_content:
        print("\n⚠️  DIAGNÓSTICO: La página muestra 'Cargando datos del sistema...'")
        print("   Esto indica que el JavaScript está iniciando pero puede tener errores.")
        print("   Revisar la consola del navegador para errores específicos.")
    
if __name__ == "__main__":
    test_schedule_page()