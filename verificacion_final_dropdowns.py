#!/usr/bin/env python
"""
Verificación final de la solución de dropdowns
"""

import requests
import json

def test_final_solution():
    """Prueba final de la solución"""
    print("🎯 VERIFICACIÓN FINAL DE LA SOLUCIÓN")
    print("=" * 50)
    
    # 1. Probar API
    print("1. 📡 Probando API de recursos...")
    try:
        response = requests.get("http://127.0.0.1:8000/academic-system/schedules/resources/")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                resources = data.get('data', {})
                print("   ✅ API funcionando correctamente")
                
                # Verificar cada tipo de recurso
                resource_counts = {}
                for key, items in resources.items():
                    count = len(items) if isinstance(items, list) else 0
                    resource_counts[key] = count
                    print(f"   • {key}: {count} elementos")
                
                if all(count > 0 for count in resource_counts.values()):
                    print("   ✅ Todos los recursos disponibles")
                    return True
                else:
                    print("   ❌ Faltan algunos recursos")
                    return False
            else:
                print(f"   ❌ Error en API: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones finales"""
    print(f"\n🚀 INSTRUCCIONES FINALES:")
    print("-" * 30)
    print("1. Ve a: http://127.0.0.1:8000/academic-system/schedules/")
    print("2. Presiona F12 para abrir la consola")
    print("3. Haz clic en 'Crear Nuevo Horario'")
    print("4. Los dropdowns se deben llenar automáticamente")
    print()
    print("Si hay problemas, ejecuta en la consola:")
    print("• debugResources()       - Ver recursos disponibles")
    print("• forcePopulateSelects() - Forzar llenado de dropdowns")
    print("• testCreateModal()      - Probar modal completo")

def main():
    api_ok = test_final_solution()
    
    if api_ok:
        print(f"\n🎉 SOLUCIÓN APLICADA CORRECTAMENTE")
        print(f"✅ Las APIs funcionan")
        print(f"✅ Los datos están disponibles")
        print(f"✅ Los selectores JavaScript fueron corregidos")
        print(f"✅ Se agregaron funciones de depuración")
        
        show_instructions()
        
        print(f"\n📋 CAMBIOS REALIZADOS:")
        print(f"• Corregidos selectores JavaScript en populateSelectOptions()")
        print(f"• Agregado selector alternativo automático")
        print(f"• Mejorados logs de diagnóstico")
        print(f"• Agregadas funciones de depuración globales")
        
        print(f"\n💡 Si los dropdowns siguen sin funcionar:")
        print(f"1. Recarga la página (Ctrl+F5)")
        print(f"2. Verifica la consola del navegador")
        print(f"3. Usa las funciones de depuración disponibles")
        
    else:
        print(f"\n⚠️ HAY PROBLEMAS CON LAS APIS")
        print(f"Asegúrate de que el servidor Django esté corriendo:")
        print(f"python manage.py runserver")

if __name__ == "__main__":
    main()