#!/usr/bin/env python3
"""
Test simple para verificar la detección de canciones
"""

import sys
import os

# Añadir el directorio app al path para importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import detect_text_type, smart_text_processing

def test_song_detection():
    """Probar la detección de canciones con varios ejemplos"""
    
    # Ejemplo 1: Canción con estribillo claro
    song1 = """Bajo la luz de la luna
    Cantando nuestra canción
    Bajo la luz de la luna
    Late fuerte el corazón
    
    Hey, hey, vamos a bailar
    La noche es para soñar
    Hey, hey, vamos a bailar
    Nunca nos vamos a parar"""
    
    # Ejemplo 2: Poema sin estructura musical
    poem1 = """En el jardín de mis sueños
    Florece la esperanza eterna
    Donde el alma encuentra paz
    Y la vida se hace tierna"""
    
    # Ejemplo 3: Texto narrativo
    narrative1 = """Había una vez un reino lejano donde los pájaros cantaban melodías mágicas. 
    El rey de ese lugar era conocido por su sabiduría y bondad. 
    Un día, llegó un viajero que traía noticias del mundo exterior."""
    
    # Ejemplo 4: Canción con interjecciones
    song2 = """Oh, oh, oh
    La la la la
    Siento el ritmo en mi corazón
    Na na na na
    Vamos a cantar esta canción"""
    
    # Ejemplo 5: Canción de rap/urbana
    song3 = """Yo soy el rey del rap, no hay quien me pare
    Con mi flow y mi beat, nadie puede competir
    Yo soy el rey del rap, mi música es mi arte
    Hasta el final voy a luchar, nunca me voy a rendir"""
    
    examples = [
        ("Canción con estribillo", song1, True),
        ("Poema", poem1, False),
        ("Narrativa", narrative1, False),
        ("Canción con interjecciones", song2, True),
        ("Canción de rap", song3, True),
    ]
    
    print("🎵 Test de Detección de Canciones")
    print("=" * 50)
    
    for name, text, expected_is_song in examples:
        analysis = detect_text_type(text)
        processing = smart_text_processing(text)
        
        is_song = analysis["is_song"]
        detected_type = analysis["type"]
        
        # Mostrar resultado
        status = "✅" if is_song == expected_is_song else "❌"
        print(f"\n{status} {name}")
        print(f"   Texto: {text[:50]}...")
        print(f"   Esperado: {'Canción' if expected_is_song else 'No canción'}")
        print(f"   Detectado: {detected_type}")
        print(f"   Es canción: {is_song}")
        print(f"   Voz sugerida: {analysis['suggested_voice']}")
        print(f"   Música sugerida: {analysis['suggested_music_style']}")
        
        if is_song:
            print(f"   Texto procesado: {processing['processed_text'][:100]}...")
    
    print("\n" + "=" * 50)
    print("Test completado.")

if __name__ == "__main__":
    test_song_detection()
