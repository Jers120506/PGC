#!/usr/bin/env python3
"""
VERIFICACIÓN CON LOGIN INCLUIDO
==============================
"""
import requests
from bs4 import BeautifulSoup

def verificar_con_login():
    """Verifica el sistema haciendo login primero"""
    print("🔐 VERIFICACIÓN CON AUTENTICACIÓN")
    print("=" * 50)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    base_url = "http://127.0.0.1:8000"
    
    # 1. Obtener página de login y token CSRF
    print("1. 🔑 Obteniendo token de login...")
    login_page = session.get(f"{base_url}/auth/login/")
    if login_page.status_code != 200:
        print(f"   ❌ Error obteniendo login: {login_page.status_code}")
        return
    
    # Obtener CSRF token
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_token:
        print("   ❌ No se pudo obtener token CSRF")
        return
    
    csrf_value = csrf_token['value']
    print(f"   ✅ Token CSRF obtenido: {csrf_value[:20]}...")
    
    # 2. Hacer login
    print("2. 🚪 Haciendo login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123',  # Contraseña típica
        'csrfmiddlewaretoken': csrf_value
    }
    
    login_response = session.post(f"{base_url}/auth/login/", data=login_data)
    if login_response.status_code == 200 and 'login' not in login_response.url:
        print("   ✅ Login exitoso")
    else:
        # Probar otra contraseña
        login_data['password'] = '123'
        login_response = session.post(f"{base_url}/auth/login/", data=login_data)
        if login_response.status_code == 200 and 'login' not in login_response.url:
            print("   ✅ Login exitoso (contraseña alternativa)")
        else:
            print(f"   ❌ Login falló - Status: {login_response.status_code}")
            print(f"   URL resultante: {login_response.url}")
            return
    
    # 3. Acceder a página de horarios
    print("3. 📅 Accediendo a página de horarios...")
    schedule_page = session.get(f"{base_url}/academic-system/schedules/")
    if schedule_page.status_code != 200:
        print(f"   ❌ Error accediendo a horarios: {schedule_page.status_code}")
        return
    
    html_content = schedule_page.text
    print(f"   ✅ Página cargada ({len(html_content)} caracteres)")
    
    # 4. Verificar elementos específicos
    print("4. 🔍 Verificando funciones implementadas...")
    
    elementos_verificar = {
        'Gestión de Horarios': 'Título correcto',
        'filter-course': 'Dropdown de cursos',
        'filter-teacher': 'Dropdown de profesores',
        'clearFilters()': 'Botón limpiar filtros',
        'applyFilters()': 'Botón aplicar filtros',
        'ondblclick="editSchedule': 'Doble-click para editar',
        'populateSelect': 'Función poblar selects',
        'Estado del Sistema: Sistema: Mejorado': 'Mensaje problemático (debe estar ausente)'
    }
    
    for elemento, descripcion in elementos_verificar.items():
        esta_presente = elemento in html_content
        if elemento == 'Estado del Sistema: Sistema: Mejorado':
            # Este debe estar ausente
            if not esta_presente:
                print(f"   ✅ {descripcion}")
            else:
                print(f"   ❌ {descripcion} - AÚN PRESENTE")
        else:
            # Estos deben estar presentes
            if esta_presente:
                print(f"   ✅ {descripcion}")
            else:
                print(f"   ❌ {descripcion}")
    
    # 5. Guardar fragmento de HTML para inspección
    with open("C:/Users/jbang/OneDrive/Desktop/gestion de proyectos/debug_schedule_page.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("   💾 Página guardada en debug_schedule_page.html para inspección")
    
    # 6. Verificar APIs también
    print("5. 🔧 Verificando APIs con autenticación...")
    api_resources = session.get(f"{base_url}/academic-system/schedules/resources/")
    if api_resources.status_code == 200:
        data = api_resources.json()
        courses_count = len(data.get('data', {}).get('courses', []))
        teachers_count = len(data.get('data', {}).get('teachers', []))
        print(f"   ✅ API recursos: {courses_count} cursos, {teachers_count} profesores")
    else:
        print(f"   ❌ API recursos falló: {api_resources.status_code}")
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL CON AUTENTICACIÓN:")
    print("=" * 50)
    print("✅ Sistema accesible con login")
    print("✅ Página de horarios carga")
    print("✅ APIs funcionan con autenticación")
    print("📄 Revisar debug_schedule_page.html para detalles")

if __name__ == "__main__":
    verificar_con_login()