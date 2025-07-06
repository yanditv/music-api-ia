#!/usr/bin/env python3
"""
Test completo de la API con ejemplos reales
"""

import requests
import json
import time

def test_api_with_examples():
    """Probar la API con ejemplos de canciones, poemas y narrativa"""
    
    base_url = "http://localhost:8000"
    
    # Ejemplos para probar
    examples = [
        {
            "name": "Canción Folk",
            "text": """En el camino encontré
una rosa que brillaba
En el camino encontré
el amor que me esperaba

Oh, oh, dulce melodía
que llena mi corazón
Oh, oh, dulce melodía
de nuestra canción""",
            "expected_type": "song"
        },
        {
            "name": "Poema Romántico", 
            "text": """En tus ojos veo el cielo
en tu sonrisa la luz
En tu alma encuentro consuelo
en tu amor mi juventud""",
            "expected_type": "poem"
        },
        {
            "name": "Canción Pop",
            "text": """Yeah, yeah, vamos a bailar
la noche es para soñar
Yeah, yeah, vamos a bailar
nunca nos vamos a parar

La la la la
Na na na na
Siente el beat
mueve los pies""",
            "expected_type": "song"
        }
    ]
    
    print("🧪 Test Completo de la API Bark")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{base_url}/voices")
        if response.status_code != 200:
            print("❌ El servidor no está corriendo. Inicia primero: python start.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Inicia primero: python start.py")
        return
    
    print("✅ Servidor conectado correctamente")
    
    for example in examples:
        print(f"\n🎯 Probando: {example['name']}")
        print(f"   Texto: {example['text'][:50]}...")
        
        # 1. Analizar el texto
        try:
            analyze_response = requests.post(
                f"{base_url}/analyze-text/",
                json={"text": example["text"]}
            )
            
            if analyze_response.status_code == 200:
                analysis = analyze_response.json()
                detected_type = analysis["analysis"]["type"]
                is_song = analysis["analysis"]["is_song"]
                
                status = "✅" if detected_type == example["expected_type"] else "❌"
                print(f"   {status} Detectado como: {detected_type}")
                print(f"   📊 Es canción: {is_song}")
                print(f"   🎤 Voz sugerida: {analysis['analysis']['suggested_voice']}")
                print(f"   🎵 Música sugerida: {analysis['analysis']['suggested_music_style']}")
                
                # 2. Generar audio con procesamiento inteligente
                smart_response = requests.post(
                    f"{base_url}/smart-generate/",
                    json={
                        "text": example["text"],
                        "voice": analysis["analysis"]["suggested_voice"]
                    }
                )
                
                if smart_response.status_code == 200:
                    result = smart_response.json()
                    print(f"   🎧 Audio generado: {result['file_id']}")
                    print(f"   📝 Texto procesado: {result['processed_text'][:80]}...")
                else:
                    print(f"   ❌ Error generando audio: {smart_response.status_code}")
                    
            else:
                print(f"   ❌ Error analizando texto: {analyze_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Test completado")
    print("💡 Tips:")
    print("   - Verifica los resultados en http://localhost:8000/docs")
    print("   - Prueba más ejemplos en http://localhost:8000/music-examples")

if __name__ == "__main__":
    test_api_with_examples()
