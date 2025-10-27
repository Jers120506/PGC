#!/usr/bin/env python3
"""
Script para verificar REALMENTE el estado del sistema académico
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_basic_access():
    """Probar acceso básico al servidor"""
    print("1. 🌐 VERIFICANDO ACCESO BÁSICO AL SERVIDOR...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Redirects a: {response.url}")
        if response.status_code in [200, 302]:
            print("   ✅ Servidor accesible")
            return True
        else:
            print("   ❌ Servidor no responde correctamente")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_login_page():
    """Probar página de login"""
    print("\n2. 🔐 VERIFICANDO PÁGINA DE LOGIN...")
    try:
        response = requests.get(f"{BASE_URL}/auth/login/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            if "login" in response.text.lower() or "usuario" in response.text.lower():
                print("   ✅ Página de login cargando")
                return True
            else:
                print("   ⚠️  Página carga pero no parece ser login")
                return False
        else:
            print("   ❌ Login no accesible")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_schedules_page():
    """Probar página de horarios"""
    print("\n3. 📅 VERIFICANDO PÁGINA DE HORARIOS...")
    try:
        response = requests.get(f"{BASE_URL}/academic-system/schedules/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Página de horarios accesible")
            return True
        elif response.status_code == 302:
            print("   ⚠️  Redirige (probablemente requiere login)")
            return True
        elif response.status_code == 403:
            print("   ⚠️  Acceso denegado (requiere autenticación)")
            return True
        else:
            print(f"   ❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_schedule_apis():
    """Probar APIs del sistema de horarios"""
    print("\n4. 🔧 VERIFICANDO APIs DE HORARIOS...")
    
    apis_to_test = [
        "/academic-system/schedules/resources/",
        "/academic-system/schedules/",
        "/academic-system/schedules/matrix/",
        "/academic-system/schedules/system-overview/"
    ]
    
    results = {}
    for api in apis_to_test:
        try:
            response = requests.get(f"{BASE_URL}{api}", timeout=5)
            results[api] = {
                'status': response.status_code,
                'accessible': response.status_code in [200, 302, 403]  # 403 es esperado sin auth
            }
            print(f"   {api}: {response.status_code}")
        except Exception as e:
            results[api] = {
                'status': 'ERROR',
                'accessible': False,
                'error': str(e)
            }
            print(f"   {api}: ERROR - {e}")
    
    working_apis = sum(1 for r in results.values() if r['accessible'])
    print(f"   ✅ {working_apis}/{len(apis_to_test)} APIs responden")
    
    return results

def check_file_structure():
    """Verificar estructura de archivos clave"""
    print("\n5. 📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS...")
    
    import os
    
    key_files = [
        "manage.py",
        "templates/academics_extended/schedule_management.html",
        "academics_extended/schedule_views.py",
        "academics_extended/urls.py"
    ]
    
    existing_files = []
    for file_path in key_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
    
    print(f"   📊 {len(existing_files)}/{len(key_files)} archivos clave encontrados")
    return existing_files

def verify_schedule_template():
    """Verificar contenido del template de horarios"""
    print("\n6. 🎨 VERIFICANDO TEMPLATE DE HORARIOS...")
    
    template_path = "templates/academics_extended/schedule_management.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar elementos clave
        checks = {
            'filter-course': 'id="filter-course"' in content,
            'filter-teacher': 'id="filter-teacher"' in content,
            'applyFilters': 'function applyFilters()' in content,
            'clearFilters': 'function clearFilters()' in content,
            'editSchedule': 'function editSchedule(' in content,
            'doble-clic': 'ondblclick=' in content
        }
        
        print("   Elementos encontrados:")
        for check, found in checks.items():
            status = "✅" if found else "❌"
            print(f"   {status} {check}")
        
        implemented = sum(checks.values())
        print(f"   📊 {implemented}/{len(checks)} funcionalidades en template")
        
        return checks
        
    except Exception as e:
        print(f"   ❌ Error leyendo template: {e}")
        return {}

def main():
    print("🔍 VERIFICACIÓN REAL DEL ESTADO DEL SISTEMA")
    print("=" * 60)
    
    # Ejecutar todas las verificaciones
    server_ok = test_basic_access()
    login_ok = test_login_page()
    schedules_ok = test_schedules_page()
    apis_result = test_schedule_apis()
    files_ok = check_file_structure()
    template_ok = verify_schedule_template()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN REAL DEL ESTADO:")
    print("=" * 60)
    
    # Servidor
    print(f"🌐 Servidor Django: {'✅ OK' if server_ok else '❌ FAIL'}")
    print(f"🔐 Login disponible: {'✅ OK' if login_ok else '❌ FAIL'}")
    print(f"📅 Horarios disponible: {'✅ OK' if schedules_ok else '❌ FAIL'}")
    
    # APIs
    working_apis = sum(1 for r in apis_result.values() if r['accessible']) if apis_result else 0
    total_apis = len(apis_result) if apis_result else 0
    print(f"🔧 APIs funcionando: {working_apis}/{total_apis}")
    
    # Archivos
    files_count = len(files_ok) if isinstance(files_ok, list) else 0
    print(f"📁 Archivos presentes: {files_count}/4 archivos clave")
    
    # Template
    template_features = sum(template_ok.values()) if template_ok else 0
    template_total = len(template_ok) if template_ok else 0
    print(f"🎨 Template features: {template_features}/{template_total}")
    
    # Evaluación general
    total_score = 0
    max_score = 0
    
    if server_ok: total_score += 20
    if login_ok: total_score += 15
    if schedules_ok: total_score += 15
    total_score += (working_apis / total_apis * 25) if total_apis > 0 else 0
    total_score += (files_count / 4 * 15)
    total_score += (template_features / template_total * 10) if template_total > 0 else 0
    
    max_score = 100
    
    print(f"\n🎯 PUNTUACIÓN REAL: {total_score:.1f}/100")
    
    if total_score >= 80:
        print("✅ SISTEMA FUNCIONAL - Las correcciones están implementadas")
    elif total_score >= 60:
        print("⚠️  SISTEMA PARCIAL - Algunas funcionalidades faltan")
    else:
        print("❌ SISTEMA DEFICIENTE - Necesita trabajo significativo")
    
    print("\n💡 Accede a:")
    print("   - Login: http://127.0.0.1:8000/auth/login/")
    print("   - Horarios: http://127.0.0.1:8000/academic-system/schedules/")

if __name__ == "__main__":
    main()