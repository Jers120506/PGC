#!/usr/bin/env python3
"""
Script para mostrar la matriz de horarios
"""

import requests
import json

def show_schedule_matrix():
    """Mostrar la matriz de horarios en formato legible"""
    print("=== MATRIZ DE HORARIOS ACADÉMICOS ===")
    
    try:
        response = requests.get("http://127.0.0.1:8000/academic-system/api/schedules/matrix/")
        data = response.json()
        
        if data.get('status') == 'success':
            matrix_data = data.get('data', {})
            matrix = matrix_data.get('matrix', [])
            
            print(f"📅 Año académico: {matrix_data.get('academic_year')}")
            print(f"📊 Total horarios: {matrix_data.get('total_schedules')}")
            print()
            
            weekdays = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes'}
            
            for slot in matrix:
                slot_info = slot['time_slot']
                print(f"🕐 {slot_info['name']} ({slot_info['start_time']}-{slot_info['end_time']}):")
                
                has_schedules = False
                for day_num in [1, 2, 3, 4, 5]:
                    if str(day_num) in slot['days']:
                        schedules = slot['days'][str(day_num)]['schedules']
                        if schedules:
                            has_schedules = True
                            for schedule in schedules:
                                print(f"  📚 {weekdays[day_num]}: {schedule['course']['name']} - {schedule['subject']['name']}")
                                print(f"      👨‍🏫 Prof: {schedule['teacher']['name']}")
                                print(f"      🏫 Salón: {schedule['classroom']['name']}")
                
                if not has_schedules:
                    print("    (Sin horarios asignados)")
                print()
        else:
            print(f"❌ Error: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    show_schedule_matrix()