from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario usando una key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_weekday_name(weekday_num):
    """Convierte el número del día de la semana al nombre"""
    weekdays = {
        1: 'Lunes',
        2: 'Martes', 
        3: 'Miércoles',
        4: 'Jueves',
        5: 'Viernes',
        6: 'Sábado',
        7: 'Domingo'
    }
    return weekdays.get(int(weekday_num), 'Desconocido')

@register.filter
def slugify_custom(value):
    """Convierte texto a formato slug personalizado"""
    import re
    value = str(value).lower()
    value = re.sub(r'[^\w\s-]', '', value)
    value = re.sub(r'[-\s]+', '-', value)
    return value