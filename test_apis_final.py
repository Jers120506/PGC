"""
Script para probar que las APIs funcionan correctamente sin errores
"""
import requests
import json

def test_api(url, description):
    try:
        print(f"\n🧪 Probando: {description}")
        print(f"📡 URL: {url}")
        
        response = requests.get(url)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'No Content-Type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON válido. Tipo: {type(data)}")
                if isinstance(data, dict) and 'status' in data:
                    print(f"📦 Status del API: {data.get('status')}")
                    if 'data' in data:
                        print(f"📊 Datos disponibles: {len(data['data']) if isinstance(data['data'], list) else 'N/A'}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Error: Respuesta no es JSON válido")
                print(f"📄 Primeros 200 caracteres: {response.text[:200]}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error de conexión: {e}")
        return False

def main():
    base_url = "http://127.0.0.1:8000/academic-system/schedules"
    
    apis = [
        (f"{base_url}/resources/", "API de Recursos"),
        (f"{base_url}/api/", "API de Lista de Horarios"),
        (f"{base_url}/matrix/", "API de Matriz de Horarios"),
        (f"{base_url}/system-overview/", "API de Resumen del Sistema"),
        (f"{base_url}/matrix/?course_id=125", "API de Matriz con Filtro (Curso 125)"),
        (f"{base_url}/matrix/?weekday=1", "API de Matriz con Filtro (Lunes)"),
        (f"{base_url}/api/?teacher_id=3", "API de Lista con Filtro (Profesor 3)"),
    ]
    
    print("🚀 Iniciando pruebas de APIs...")
    print("="*50)
    
    results = []
    for url, description in apis:
        result = test_api(url, description)
        results.append((description, result))
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE RESULTADOS:")
    print("="*50)
    
    passed = 0
    for desc, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {desc}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado final: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las APIs funcionan correctamente!")
    else:
        print("⚠️ Algunas APIs tienen problemas")

if __name__ == "__main__":
    main()