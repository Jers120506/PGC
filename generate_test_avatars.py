import os
import django
from PIL import Image, ImageDraw, ImageFont
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

def create_avatar_image(initials, background_color, text_color, size=(200, 200)):
    """Crear una imagen de avatar con iniciales"""
    # Crear imagen
    img = Image.new('RGB', size, color=background_color)
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente, si no usar la default
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Obtener dimensiones del texto
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Centrar el texto
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Dibujar el texto
    draw.text((x, y), initials, fill=text_color, font=font)
    
    return img

def generate_test_avatars():
    """Generar avatares de prueba para los usuarios"""
    print("=== Generando avatares de prueba ===")
    
    users_info = [
        {'username': 'admin', 'initials': 'MJ', 'color': '#e74c3c', 'text': '#ffffff'},
        {'username': 'secretario', 'initials': 'ME', 'color': '#3498db', 'text': '#ffffff'},
        {'username': 'profesor', 'initials': 'CA', 'color': '#2ecc71', 'text': '#ffffff'},
        {'username': 'ana', 'initials': 'AC', 'color': '#f39c12', 'text': '#ffffff'},
    ]
    
    media_dir = 'media/avatars'
    os.makedirs(media_dir, exist_ok=True)
    
    for user_info in users_info:
        try:
            # Crear imagen
            img = create_avatar_image(
                user_info['initials'], 
                user_info['color'], 
                user_info['text']
            )
            
            # Guardar imagen
            filename = f"{user_info['username']}_avatar.png"
            filepath = os.path.join(media_dir, filename)
            img.save(filepath, 'PNG')
            
            print(f"✅ Avatar creado para {user_info['username']}: {filename}")
            
        except Exception as e:
            print(f"❌ Error creando avatar para {user_info['username']}: {e}")
    
    print(f"\n📂 Avatares guardados en: {os.path.abspath(media_dir)}")
    
    # Listar archivos creados
    avatars = [f for f in os.listdir(media_dir) if f.endswith('.png')]
    print(f"📸 Avatares disponibles: {avatars}")

if __name__ == "__main__":
    generate_test_avatars()