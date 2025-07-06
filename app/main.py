from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from .bark_utils import generate_audio  # Funcionalidad Bark
import os
import uuid
from typing import Optional, Any

app = FastAPI(
    title="Bark Text-to-Speech API", 
    version="1.0.0",
    description="API para generar audio usando el modelo Bark de Suno AI"
)

class AudioRequest(BaseModel):
    text: str
    voice: Optional[str] = "v2/es_speaker_0"  # Voz predeterminada
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Desde el primer latido en tu corazón\\nSupe que Dios me hablaba en una canción\\nFuiste un milagro que bajó del cielo\\nMi pequeño sol, mi mayor anhelo",
                "voice": "v2/es_speaker_2"
            }
        }

class AudioResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    voice_used: str
    detected_type: Optional[str] = None
    analysis_notes: Optional[list] = None

class MusicRequest(BaseModel):
    text: str
    voice: Optional[str] = "v2/es_speaker_0"
    include_music: Optional[bool] = False
    music_style: Optional[str] = "background"  # "background", "melody", "upbeat", "calm"
    
    class Config:
        schema_extra = {
            "example": {
                "text": "La la la, canta conmigo\\nEsta es una canción feliz\\nLa la la, todo está bien",
                "voice": "v2/es_speaker_1",
                "include_music": True,
                "music_style": "melody"
            }
        }

class MusicResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    voice_used: str
    music_included: bool
    music_style: str

# Directorio para archivos generados
AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Endpoint de bienvenida con información sobre la API"""
    return {
        "message": "🧠 Bark Text-to-Speech API con IA Integrada",
        "version": "2.0.0",
        "features": [
            "🧠 Detección automática de texto (poemas, canciones, narrativas)",
            "🎵 Música inteligente según el tipo de contenido",
            "🗣️ Selección automática de voz óptima",
            "⚡ Procesamiento optimizado para cada tipo de texto"
        ],
        "endpoints": {
            "POST /generate/": "🧠 Generar audio con IA (descarga directa)",
            "POST /generate-info/": "🧠 Generar audio con IA (información JSON)",
            "POST /generate-music/": "🎵 Generar con música personalizable + IA",
            "POST /smart-generate/": "🤖 Generación con IA COMPLETA (recomendado)",
            "POST /paste-text/": "🍃 Pegar texto plano sin problemas de JSON",
            "POST /analyze-text/": "🔍 Solo analizar texto sin generar audio",
            "GET /download/{file_id}": "📥 Descargar archivo de audio generado",
            "GET /health": "💚 Estado de salud de la API",
            "GET /voices": "🗣️ Lista de voces disponibles",
            "GET /music-examples": "🎵 Ejemplos de generación de música"
        },
        "tips_for_swagger": {
            "multiline_text": "Para texto con saltos de línea, usa \\n en lugar de saltos reales",
            "ejemplo_poema": "Desde el primer latido\\nSupe que Dios me hablaba\\nFuiste un milagro",
            "alternative": "O usa /paste-text/ con curl para texto plano sin escapes"
        },
        "recommendation": "Usa /smart-generate/ para la mejor experiencia automática"
    }

@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    return {
        "status": "healthy",
        "service": "bark-api",
        "message": "API funcionando correctamente"
    }

@app.get("/voices")
async def list_voices():
    """Lista de voces disponibles en Bark"""
    voices = {
        "english": [
            "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2", 
            "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
            "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8", "v2/en_speaker_9"
        ],
        "spanish": [
            "v2/es_speaker_0", "v2/es_speaker_1", "v2/es_speaker_2",
            "v2/es_speaker_3", "v2/es_speaker_4", "v2/es_speaker_5",
            "v2/es_speaker_6", "v2/es_speaker_7", "v2/es_speaker_8", "v2/es_speaker_9"
        ],
        "other_languages": [
            "v2/zh_speaker_0", "v2/zh_speaker_1", "v2/zh_speaker_2",
            "v2/fr_speaker_0", "v2/fr_speaker_1", "v2/fr_speaker_2",
            "v2/de_speaker_0", "v2/de_speaker_1", "v2/de_speaker_2",
            "v2/hi_speaker_0", "v2/hi_speaker_1", "v2/hi_speaker_2",
            "v2/it_speaker_0", "v2/it_speaker_1", "v2/it_speaker_2",
            "v2/ja_speaker_0", "v2/ja_speaker_1", "v2/ja_speaker_2",
            "v2/ko_speaker_0", "v2/ko_speaker_1", "v2/ko_speaker_2",
            "v2/pl_speaker_0", "v2/pl_speaker_1", "v2/pl_speaker_2",
            "v2/pt_speaker_0", "v2/pt_speaker_1", "v2/pt_speaker_2",
            "v2/ru_speaker_0", "v2/ru_speaker_1", "v2/ru_speaker_2",
            "v2/tr_speaker_0", "v2/tr_speaker_1", "v2/tr_speaker_2"
        ]
    }
    return {
        "voices": voices,
        "note": "Usa cualquiera de estas voces en el campo 'voice' de tu petición"
    }

@app.post("/generate/", response_class=FileResponse)
async def generate_speech_file(request: AudioRequest):
    """
    Generar y descargar audio directamente con detección inteligente (ideal para curl)
    
    - **text**: El texto que quieres convertir a audio (poemas, canciones, etc.)
    - **voice**: La voz a usar (opcional, por defecto v2/es_speaker_0)
    
    🧠 INCLUYE DETECCIÓN AUTOMÁTICA: El sistema detecta si es poema, canción o narrativa
    y optimiza automáticamente el procesamiento para mejor calidad de audio.
    """
    file_id, audio_path, analysis_info = await _generate_audio_internal(request, use_smart_processing=True)
    
    # Añadir información del análisis al nombre del archivo
    text_type = analysis_info["type"] if analysis_info else "text"
    
    return FileResponse(
        audio_path, 
        media_type="audio/wav",
        filename=f"bark_{text_type}_{file_id}.wav"
    )

@app.post("/generate-info/", response_model=AudioResponse)
async def generate_speech_info(request: AudioRequest):
    """
    Generar audio con detección inteligente y obtener información (ideal para interfaces web)
    
    - **text**: El texto que quieres convertir a audio (poemas, canciones, etc.)
    - **voice**: La voz a usar (opcional, por defecto v2/es_speaker_0)
    
    🧠 INCLUYE DETECCIÓN AUTOMÁTICA: Analiza tu texto y aplica la mejor configuración.
    Devuelve información sobre el archivo generado y el análisis realizado.
    """
    file_id, audio_path, analysis_info = await _generate_audio_internal(request, use_smart_processing=True)
    
    text_type = analysis_info["type"] if analysis_info else "text"
    analysis_notes = analysis_info["processing_notes"] if analysis_info else []
    
    return AudioResponse(
        message=f"Audio generado con detección automática - Tipo detectado: {text_type}",
        file_id=file_id,
        filename=f"bark_{text_type}_{file_id}.wav",
        voice_used=request.voice,
        detected_type=text_type,
        analysis_notes=analysis_notes
    )

@app.get("/download/{file_id}", response_class=FileResponse)
async def download_audio(file_id: str):
    """
    Descargar un archivo de audio generado previamente
    """
    audio_path = os.path.join(AUDIO_DIR, f"{file_id}.wav")
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")
    
    return FileResponse(
        audio_path,
        media_type="audio/wav", 
        filename=f"bark_audio_{file_id}.wav"
    )

@app.post("/generate-music/", response_model=MusicResponse)
async def generate_music(request: MusicRequest):
    """
    Generar audio con música usando detección inteligente de Bark
    
    - **text**: El texto/letra que quieres convertir a audio
    - **voice**: La voz a usar (opcional, por defecto v2/es_speaker_0)
    - **include_music**: Si incluir música de fondo (opcional, se auto-detecta)
    - **music_style**: Estilo de música (opcional, se auto-detecta el mejor)
    
    🧠 DETECCIÓN INTELIGENTE: Si no especificas música, el sistema detecta automáticamente
    si tu texto es un poema o canción y añade la música apropiada.
    """
    try:
        # Validar que el texto no esté vacío
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
        
        # Usar detección inteligente para mejorar configuración automática
        from . import smart_text_processing
        analysis_result = smart_text_processing(request.text)
        analysis = analysis_result["analysis"]
        auto_recommendations = analysis_result["recommendations"]
        
        # Usar configuración del usuario o recomendaciones automáticas
        include_music = request.include_music if request.include_music is not None else auto_recommendations["include_music"]
        music_style = request.music_style if request.music_style != "background" else auto_recommendations["music_style"]
        optimal_voice = request.voice if request.voice != "v2/es_speaker_0" else auto_recommendations["voice"]
        
        print(f"🧠 Análisis musical: {analysis['type']} → música: {include_music}, estilo: {music_style}")
        
        # Preparar el texto con tokens musicales
        music_text = _prepare_music_text(request.text, include_music, music_style)
        
        # Crear una versión modificada del request
        audio_request = AudioRequest(text=music_text, voice=optimal_voice)
        
        # Generar el audio (sin procesamiento inteligente adicional ya que ya se aplicó)
        file_id, audio_path, _ = await _generate_audio_internal(audio_request, use_smart_processing=False)
        
        return MusicResponse(
            message=f"Audio con música generado - Tipo detectado: {analysis['type']}",
            file_id=file_id,
            filename=f"bark_music_{analysis['type']}_{file_id}.wav",
            voice_used=optimal_voice,
            music_included=include_music,
            music_style=music_style
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generando música: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/music-examples")
async def music_examples():
    """Ejemplos de cómo generar música con Bark"""
    return {
        "music_capabilities": {
            "supported": [
                "Música de fondo simple",
                "Melodías básicas", 
                "Efectos sonoros",
                "Combinación voz + música"
            ],
            "limitations": [
                "No instrumentos específicos complejos",
                "No armonías elaboradas",
                "Calidad musical básica"
            ]
        },
        "music_styles": {
            "background": "Música suave de fondo",
            "melody": "Melodía simple",
            "upbeat": "Música alegre/enérgica", 
            "calm": "Música relajante"
        },
        "examples": {
            "simple_song": {
                "text": "La la la, canta conmigo\nEsta es una canción feliz\nLa la la, todo está bien\nLa la la, canta conmigo",
                "voice": "v2/es_speaker_2",
                "include_music": True,
                "music_style": "melody"
            },
            "upbeat_song": {
                "text": "¡Vamos a bailar!\n¡La fiesta comenzó!\n¡Todos a cantar!\n¡Vamos a bailar!",
                "voice": "v2/es_speaker_1",
                "include_music": True, 
                "music_style": "upbeat"
            },
            "chorus_song": {
                "text": "En el cielo las estrellas\nBrillan con amor\nEn el cielo las estrellas\nBrillan con amor\nCanta conmigo esta canción\nCanta conmigo esta canción",
                "voice": "v2/es_speaker_2",
                "include_music": True,
                "music_style": "melody"
            },
            "background_music": {
                "text": "Bienvenidos a nuestro programa de radio con música relajante de fondo",
                "voice": "v2/es_speaker_0", 
                "include_music": True,
                "music_style": "background"
            }
        },
        "tips": [
            "Para canciones: usa líneas repetidas (estribillos) para mejor efecto musical",
            "Para canciones: mantén las líneas cortas (4-8 palabras por línea)",
            "Para melodías: incluye 'la la la', 'hey', 'oh' para mejor musicalidad",
            "Los estilos 'melody' y 'upbeat' funcionan mejor con letras repetitivas",
            "El estilo 'background' es ideal para locuciones", 
            "Para canciones alegres: usa ¡exclamaciones! y palabras como 'bailar', 'cantar'",
            "Experimenta con diferentes voces para diferentes efectos"
        ]
    }

@app.post("/smart-generate/", response_model=MusicResponse)
async def smart_generate(request: AudioRequest):
    """
    Generar audio con detección inteligente COMPLETA del tipo de texto
    
    - **text**: El texto que quieres convertir (poema, canción, narrativa, etc.)
    - **voice**: La voz a usar (opcional, se auto-detectará la mejor)
    
    🧠 MÁXIMA INTELIGENCIA: Este endpoint analiza automáticamente tu texto y aplica
    la configuración ÓPTIMA (voz, música, procesamiento) sin que tengas que configurar nada.
    """
    try:
        # Validar que el texto no esté vacío
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
        
        # Análisis inteligente completo del texto
        from . import smart_text_processing
        analysis_result = smart_text_processing(request.text)
        
        analysis = analysis_result["analysis"]
        recommendations = analysis_result["recommendations"]
        processed_text = analysis_result["processed_text"]
        
        print(f"🧠 Análisis inteligente completo:")
        print(f"   Tipo detectado: {analysis['type']}")
        print(f"   Líneas: {analysis['line_count']}")
        print(f"   Recomendaciones: voz={recommendations['voice']}, música={recommendations['include_music']}")
        
        # Usar las recomendaciones automáticas o la voz especificada
        optimal_voice = request.voice if request.voice != "v2/es_speaker_0" else recommendations["voice"]
        
        # Preparar texto con música si es recomendado
        final_text = processed_text
        if recommendations["include_music"]:
            final_text = _prepare_music_text(processed_text, True, recommendations["music_style"])
        
        # Generar el audio con configuración optimizada (sin procesamiento adicional)
        audio_request = AudioRequest(text=final_text, voice=optimal_voice)
        file_id, audio_path, _ = await _generate_audio_internal(audio_request, use_smart_processing=False)
        
        return MusicResponse(
            message=f"Audio generado con IA completa - Tipo: {analysis['type']}",
            file_id=file_id,
            filename=f"bark_smart_{analysis['type']}_{file_id}.wav",
            voice_used=optimal_voice,
            music_included=recommendations["include_music"],
            music_style=recommendations["music_style"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en generación inteligente: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/analyze-text/")
async def analyze_text(request: AudioRequest):
    """
    Analizar un texto para ver qué tipo es y qué configuración se recomienda
    
    - **text**: El texto a analizar
    
    Devuelve análisis detallado sin generar audio.
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
        
        from . import smart_text_processing
        analysis_result = smart_text_processing(request.text)
        
        return {
            "original_text": request.text,
            "analysis": analysis_result["analysis"],
            "recommendations": analysis_result["recommendations"],
            "processed_text": analysis_result["processed_text"],
            "example_request": {
                "text": analysis_result["processed_text"],
                "voice": analysis_result["recommendations"]["voice"],
                "include_music": analysis_result["recommendations"]["include_music"],
                "music_style": analysis_result["recommendations"]["music_style"]
            }
        }
        
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

def _prepare_music_text(text: str, include_music: bool, music_style: str) -> str:
    """Preparar texto con tokens musicales avanzados para Bark"""
    
    if not include_music:
        return text
    
    # Tokens musicales más efectivos que Bark reconoce mejor
    music_tokens = {
        "background": "[music] ",
        "melody": "♪ [music] ♪ ",
        "upbeat": "♪♪ [upbeat music] ♪♪ ",
        "calm": "[soft music] ",
    }
    
    # Prefijo musical según el estilo
    music_prefix = music_tokens.get(music_style, "[music] ")
    
    # Limpiar el texto
    clean_text = text.strip()
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    
    # Formatear para música según el estilo
    if music_style == "melody":
        # Para melodías, crear estructura musical más clara
        music_lines = []
        for i, line in enumerate(lines):
            if line.strip():
                # Alternar intensidad musical
                if i % 2 == 0:
                    music_lines.append(f"♪ {line} ♪")
                else:
                    music_lines.append(f"♪♪ {line} ♪♪")
        return " ... ".join(music_lines)
    
    elif music_style == "upbeat":
        # Para música alegre, más énfasis
        music_lines = []
        for line in lines:
            if line.strip():
                music_lines.append(f"♪♪ [music] {line} [music] ♪♪")
        return " ♪ ".join(music_lines)
    
    elif music_style == "background":
        # Para música de fondo, más sutil
        return f"[music] {clean_text}"
    
    else:  # calm
        # Para música suave
        return f"[soft music] {clean_text}"
        
async def _generate_audio_internal(request: AudioRequest, use_smart_processing: bool = True):
    """Función interna para generar audio (reutilizable) con procesamiento inteligente"""
    try:
        # Validar que el texto no esté vacío
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
        
        processed_text = request.text
        analysis_info = None
        
        # Aplicar procesamiento inteligente si está habilitado
        if use_smart_processing:
            from . import smart_text_processing
            analysis_result = smart_text_processing(request.text)
            processed_text = analysis_result["processed_text"]
            analysis_info = analysis_result["analysis"]
            
            print(f"🧠 Detección automática: {analysis_info['type']} ({analysis_info['line_count']} líneas)")
            for note in analysis_info['processing_notes']:
                print(f"   📝 {note}")
        
        # Limpiar y normalizar el texto procesado
        clean_text = processed_text.strip()
        # Reemplazar múltiples saltos de línea por uno solo (solo si no es procesamiento inteligente)
        if not use_smart_processing:
            clean_text = '\n'.join(line.strip() for line in clean_text.split('\n') if line.strip())
        
        # Generar un ID único para el archivo
        file_id = str(uuid.uuid4())
        output_file = os.path.join(AUDIO_DIR, f"{file_id}.wav")
        
        print(f"🎵 Generando audio para: '{clean_text[:50]}...' con voz: {request.voice}")
        
        # Generar el audio con el texto procesado
        audio_path = generate_audio(clean_text, request.voice, output_file)
        
        # Verificar que el archivo se creó
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo de audio")
        
        return file_id, audio_path, analysis_info
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generando audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/paste-text/", response_model=MusicResponse)
async def paste_text_generate(text_data: str = None):
    """
    🍃 Endpoint especial para pegar texto directamente sin problemas de JSON
    
    Envía el texto como texto plano en el cuerpo de la petición.
    Perfecto para copiar y pegar poemas largos sin preocuparse por escapar caracteres.
    
    Ejemplo de uso con curl:
    ```
    curl -X POST http://localhost:8000/paste-text/ \
      -H "Content-Type: text/plain" \
      -d "Tu poema completo aquí
    con saltos de línea normales
    sin necesidad de \\n"
    ```
    """
    try:
        if not text_data or not text_data.strip():
            raise HTTPException(status_code=400, detail="Texto vacío. Envía tu texto en el cuerpo de la petición.")
        
        # Crear un AudioRequest con el texto recibido
        request = AudioRequest(text=text_data.strip())
        
        # Usar el sistema inteligente completo
        from . import smart_text_processing
        analysis_result = smart_text_processing(request.text)
        
        analysis = analysis_result["analysis"]
        recommendations = analysis_result["recommendations"]
        processed_text = analysis_result["processed_text"]
        
        print(f"🍃 Texto pegado - Tipo detectado: {analysis['type']}")
        
        # Usar recomendaciones automáticas
        optimal_voice = recommendations["voice"]
        
        # Preparar texto con música si es recomendado
        final_text = processed_text
        if recommendations["include_music"]:
            final_text = _prepare_music_text(processed_text, True, recommendations["music_style"])
        
        # Generar el audio
        audio_request = AudioRequest(text=final_text, voice=optimal_voice)
        file_id, audio_path, _ = await _generate_audio_internal(audio_request, use_smart_processing=False)
        
        return MusicResponse(
            message=f"Texto pegado procesado - Tipo: {analysis['type']}",
            file_id=file_id,
            filename=f"bark_pasted_{analysis['type']}_{file_id}.wav",
            voice_used=optimal_voice,
            music_included=recommendations["include_music"],
            music_style=recommendations["music_style"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error procesando texto pegado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/paste-text-body/", response_model=MusicResponse)
async def paste_text_from_body(request: Request):
    """
    🍃 Endpoint alternativo para texto plano desde el cuerpo de la petición
    
    Acepta texto plano directamente en el cuerpo HTTP.
    """
    try:
        # Leer el cuerpo de la petición como texto plano
        body_bytes = await request.body()
        text_data = body_bytes.decode('utf-8')
        
        if not text_data or not text_data.strip():
            raise HTTPException(status_code=400, detail="Texto vacío en el cuerpo de la petición.")
        
        # Redirigir al endpoint principal
        return await paste_text_generate(text_data)
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error decodificando el texto. Asegúrate de usar UTF-8.")
    except Exception as e:
        print(f"❌ Error procesando cuerpo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor Bark API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)