"""
Bark Text-to-Speech API con capacidades musicales
"""

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Iniciar el servidor de la API Bark"""
    import uvicorn
    print("🚀 Iniciando Bark Text-to-Speech API...")
    print(f"📡 Servidor disponible en: http://{host}:{port}")
    print("📚 Documentación en: http://localhost:8000/docs")
    print("🎵 Ejemplos de música en: http://localhost:8000/music-examples")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)

def start():
    """Comando simplificado para iniciar el servidor"""
    start_server()

# Para uso directo: python -m app
if __name__ == "__main__":
    start()

import re
from typing import Dict, Any

def detect_text_type(text: str) -> Dict[str, Any]:
    """
    Detectar el tipo de texto y sus características
    """
    text = text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    analysis = {
        "text": text,
        "type": "unknown",
        "is_poem": False,
        "is_song": False,
        "is_multiline": len(lines) > 1,
        "line_count": len(lines),
        "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
        "has_rhyme_pattern": False,
        "is_narrative": False,
        "suggested_voice": "v2/es_speaker_0",
        "suggested_music_style": "background",
        "processing_notes": []
    }
    
    # Detectar si es una canción PRIMERO (más específico)
    if _is_song(text, lines):
        analysis["type"] = "song"
        analysis["is_song"] = True
        analysis["suggested_voice"] = "v2/es_speaker_1"
        analysis["suggested_music_style"] = "melody"
        analysis["processing_notes"].append("Detectado como canción - se recomienda melodía")
    
    # Detectar si es un poema (después de descartar canciones)
    elif _is_poem(text, lines):
        analysis["type"] = "poem"
        analysis["is_poem"] = True
        analysis["suggested_voice"] = "v2/es_speaker_2"  # Voz más expresiva
        analysis["suggested_music_style"] = "background"
        analysis["processing_notes"].append("Detectado como poema - se recomienda música de fondo")
    
    # Detectar narrativa
    elif _is_narrative(text, lines):
        analysis["type"] = "narrative"
        analysis["is_narrative"] = True
        analysis["suggested_voice"] = "v2/es_speaker_0"
        analysis["suggested_music_style"] = "calm"
        analysis["processing_notes"].append("Detectado como narrativa - se recomienda música suave")
    
    else:
        analysis["type"] = "text"
        analysis["processing_notes"].append("Texto general - configuración estándar")
    
    # Detectar patrones de rima
    analysis["has_rhyme_pattern"] = _detect_rhyme_pattern(lines)
    
    return analysis

def _is_poem(text: str, lines: list) -> bool:
    """Detectar si el texto es un poema"""
    if len(lines) < 2:
        return False
    
    # Características de poemas
    poem_indicators = 0
    text_lower = text.lower()
    
    # 1. Líneas de longitud similar
    line_lengths = [len(line) for line in lines]
    avg_length = sum(line_lengths) / len(line_lengths)
    similar_lengths = sum(1 for length in line_lengths if abs(length - avg_length) < 20)
    if similar_lengths / len(lines) > 0.6:
        poem_indicators += 1
    
    # 2. Posibles rimas (terminaciones similares)
    if _detect_rhyme_pattern(lines):
        poem_indicators += 2
    
    # 3. Palabras emotivas/poéticas (no musicales)
    poetic_words = [
        'corazón', 'alma', 'amor', 'vida', 'cielo', 'sol', 'luna', 'estrella',
        'sueño', 'esperanza', 'milagro', 'anhelo', 'verdad', 'eternidad',
        'jardín', 'florece', 'paz', 'tierna', 'suave', 'sublime'
    ]
    poetic_count = sum(1 for word in poetic_words if word in text_lower)
    if poetic_count >= 2:
        poem_indicators += 1
    
    # 4. Estructura estrófica (grupos de líneas separados)
    if '\n\n' in text:
        poem_indicators += 1
    
    # 5. Líneas de longitud media (no muy cortas como canciones)
    medium_lines = sum(1 for line in lines if 6 <= len(line.split()) <= 12)
    if medium_lines / len(lines) > 0.5:
        poem_indicators += 1
    
    # 6. NO tiene indicadores fuertes de canción
    strong_music_words = [
        'la la la', 'tra la la', 'na na na', 'canción', 'cantar', 'cantando',
        'rock', 'pop', 'rap', 'beat', 'bailar', 'dance'
    ]
    has_music_words = any(word in text_lower for word in strong_music_words)
    
    # Verificar repetición de líneas (típico de canciones)
    line_counts = {}
    for line in lines:
        clean_line = line.strip().lower()
        if len(clean_line) > 3:
            line_counts[clean_line] = line_counts.get(clean_line, 0) + 1
    
    has_repeated_lines = any(count > 1 for count in line_counts.values())
    
    # Si tiene indicadores fuertes de canción, no es poema
    if has_music_words or has_repeated_lines:
        return False
    
    return poem_indicators >= 2
    poetic_words = [
        'corazón', 'alma', 'amor', 'vida', 'cielo', 'sol', 'luna', 'estrella',
        'sueño', 'esperanza', 'milagro', 'anhelo', 'verdad', 'eternidad'
    ]
    text_lower = text.lower()
    poetic_count = sum(1 for word in poetic_words if word in text_lower)
    if poetic_count >= 2:
        poem_indicators += 1
    
    # 4. Estructura estrófica (grupos de líneas separados)
    if '\n\n' in text:
        poem_indicators += 1
    
    return poem_indicators >= 2

def _is_song(text: str, lines: list) -> bool:
    """Detectar si el texto es una canción con análisis avanzado"""
    if len(lines) < 2:
        return False
    
    song_indicators = 0
    text_lower = text.lower()
    
    # 1. Palabras explícitamente musicales DIRECTAS (peso muy alto)
    direct_music_words = [
        'la la la', 'tra la la', 'na na na', 'canción', 'cantar', 'cantando',
        'rock', 'pop', 'rap', 'beat', 'guitar', 'piano', 'dance', 'swing',
        'blues', 'jazz', 'reggae', 'salsa', 'tango', 'banda', 'concierto'
    ]
    direct_music_count = sum(1 for word in direct_music_words if word in text_lower)
    if direct_music_count >= 1:
        song_indicators += 5  # Muy fuerte indicador
    
    # 2. Interjecciones musicales múltiples
    musical_interjections = [
        'oh', 'ah', 'eh', 'hey', 'yeah', 'sí', 'no', 'wow', 'uoh', 'mmm',
        'lalala', 'nanana', 'dadada', 'bababa', 'yay', 'woah', 'whoa'
    ]
    interjection_lines = sum(1 for line in lines 
                           if any(interj in line.lower() for interj in musical_interjections))
    if interjection_lines >= 2:
        song_indicators += 3
    
    # 3. Repetición exacta de líneas completas (estribillos) - MUY IMPORTANTE
    repeated_lines = _count_repeated_lines(lines)
    if repeated_lines >= 1:
        song_indicators += 4  # Fuerte indicador de canción
    
    # 4. Estructura verso-estribillo detectada
    if _detect_verse_chorus_structure(lines):
        song_indicators += 3
    
    # 5. Palabras exclusivamente musicales (no narrativas)
    exclusive_music_words = [
        'bailar', 'fiesta', 'ritmo', 'melodía', 'coro', 'estribillo',
        'verso', 'compás', 'acorde', 'escenario'
    ]
    exclusive_count = sum(1 for word in exclusive_music_words if word in text_lower)
    if exclusive_count >= 1:
        song_indicators += 2
    
    # 6. Líneas muy cortas y rítmicas
    very_short_lines = sum(1 for line in lines if 2 <= len(line.split()) <= 5)
    if very_short_lines >= 2:
        song_indicators += 1
    
    # 7. Detectar si NO es narrativa (evitar falsos positivos)
    narrative_indicators = [
        'había una vez', 'érase una vez', 'en un lugar', 'entonces',
        'después', 'finalmente', 'al principio', 'historia', 'cuento',
        'reino', 'viajero', 'llegó', 'conocido por'
    ]
    
    narrative_count = sum(1 for indicator in narrative_indicators if indicator in text_lower)
    if narrative_count >= 2:
        song_indicators -= 3  # Penalizar si parece narrativa
    
    # 8. Palabras que podrían ser ambiguas - solo contar si hay otros indicadores
    ambiguous_music_words = ['música', 'cantar', 'cantaban']  # Pueden aparecer en narrativas
    if song_indicators >= 2:  # Solo si ya hay otros indicadores fuertes
        ambiguous_count = sum(1 for word in ambiguous_music_words if word in text_lower)
        song_indicators += min(ambiguous_count, 1)  # Máximo 1 punto por ambiguas
    
    # Umbral más estricto para evitar falsos positivos
    return song_indicators >= 5

def _is_narrative(text: str, lines: list) -> bool:
    """Detectar si el texto es narrativo"""
    narrative_indicators = [
        'había una vez', 'érase una vez', 'en un lugar', 'entonces',
        'después', 'finalmente', 'al principio', 'historia', 'cuento'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in narrative_indicators)

def _detect_rhyme_pattern(lines: list) -> bool:
    """Detectar posibles patrones de rima"""
    if len(lines) < 2:
        return False
    
    # Obtener las últimas 2-3 sílabas de cada línea
    endings = []
    for line in lines:
        words = line.split()
        if words:
            last_word = words[-1].lower()
            # Quitar puntuación
            last_word = re.sub(r'[^\w]', '', last_word)
            if len(last_word) >= 3:
                endings.append(last_word[-3:])
            elif len(last_word) >= 2:
                endings.append(last_word[-2:])
    
    # Buscar similitudes en las terminaciones
    similar_endings = 0
    for i in range(len(endings)):
        for j in range(i + 1, len(endings)):
            if endings[i] == endings[j]:
                similar_endings += 1
    
    return similar_endings >= 1

def smart_text_processing(text: str) -> Dict[str, Any]:
    """
    Procesamiento inteligente del texto copiado/pegado
    """
    # Analizar el texto
    analysis = detect_text_type(text)
    
    # Sugerir configuración óptima
    recommendations = {
        "voice": analysis["suggested_voice"],
        "music_style": analysis["suggested_music_style"],
        "include_music": analysis["is_poem"] or analysis["is_song"],
        "processing_strategy": _get_processing_strategy(analysis),
        "split_strategy": _get_split_strategy(analysis)
    }
    
    return {
        "analysis": analysis,
        "recommendations": recommendations,
        "processed_text": _process_text_for_audio(text, analysis)
    }

def _get_processing_strategy(analysis: Dict) -> str:
    """Determinar la mejor estrategia de procesamiento"""
    if analysis["is_poem"]:
        return "poem_with_pauses"
    elif analysis["is_song"]:
        return "song_with_rhythm"
    elif analysis["is_narrative"]:
        return "narrative_flow"
    else:
        return "standard"

def _get_split_strategy(analysis: Dict) -> str:
    """Determinar si dividir el texto en partes"""
    if analysis["line_count"] > 8:
        return "split_by_stanzas"
    elif analysis["line_count"] > 4:
        return "split_by_lines"
    else:
        return "keep_together"

def _process_text_for_audio(text: str, analysis: Dict) -> str:
    """Procesar el texto para mejor síntesis de audio"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if analysis["is_song"]:
        return _process_song_text(lines, text)
    elif analysis["is_poem"]:
        return _process_poem_text(lines, text)
    else:
        # Para texto general, flujo natural
        return " ".join(lines)

def _process_song_text(lines: list, original_text: str) -> str:
    """Procesamiento especializado para canciones"""
    # Identificar líneas repetidas (estribillos)
    line_counts = {}
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            line_counts[clean_line] = line_counts.get(clean_line, 0) + 1
    
    processed_lines = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        is_chorus = line_counts.get(line, 0) > 1
        is_last_line = i == len(lines) - 1
        
        # Procesamiento especial para estribillos
        if is_chorus:
            # Añadir tokens musicales para enfatizar el estribillo
            processed_line = f"♪ {line} ♪"
        else:
            # Verso normal - añadir ligero ritmo
            processed_line = line
        
        processed_lines.append(processed_line)
        
        # Añadir pausas musicales estratégicas
        if not is_last_line:
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            next_is_chorus = line_counts.get(next_line, 0) > 1
            
            # Pausa larga antes de estribillo
            if next_is_chorus and not is_chorus:
                processed_lines.append("... ♪ ...")
            # Pausa media después de estribillo
            elif is_chorus and not next_is_chorus:
                processed_lines.append("♪ ... ♪")
            # Pausa entre versos (cada cierta cantidad de líneas)
            elif (i + 1) % 4 == 0:
                processed_lines.append("♪ ...")
            # Pausa corta normal
            else:
                processed_lines.append("♪")
    
    return " ".join(processed_lines)

def _process_poem_text(lines: list, original_text: str) -> str:
    """Procesamiento especializado para poemas"""
    processed_lines = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        processed_lines.append(line)
        
        # Pausas contemplativas entre versos
        if i < len(lines) - 1:
            # Pausa larga entre estrofas (detectar por líneas vacías o cada 4 líneas)
            if '\n\n' in original_text or (i + 1) % 4 == 0:
                processed_lines.append("...")  # Pausa contemplativa larga
            else:
                processed_lines.append(",")    # Pausa suave entre líneas
    
    return " ".join(processed_lines)

def normalize_text_input(text: str) -> str:
    """
    Normalizar texto de entrada para manejar diferentes formatos
    """
    if not text:
        return ""
    
    # Manejar diferentes tipos de saltos de línea
    text = text.replace('\r\n', '\n')  # Windows
    text = text.replace('\r', '\n')    # Mac antiguo
    
    # Limpiar espacios extra pero preservar estructura
    lines = []
    for line in text.split('\n'):
        cleaned_line = line.strip()
        if cleaned_line:
            lines.append(cleaned_line)
        elif lines and lines[-1]:  # Preservar líneas vacías entre estrofas
            lines.append('')
    
    return '\n'.join(lines).strip()

def text_from_any_format(input_data: Any) -> str:
    """
    Extraer texto desde cualquier formato de entrada
    """
    if isinstance(input_data, str):
        return normalize_text_input(input_data)
    elif isinstance(input_data, dict) and 'text' in input_data:
        return normalize_text_input(input_data['text'])
    elif hasattr(input_data, 'text'):
        return normalize_text_input(input_data.text)
    else:
        return str(input_data).strip()

def _count_repeated_lines(lines: list) -> int:
    """Contar líneas que se repiten exactamente (estribillos)"""
    line_counts = {}
    for line in lines:
        clean_line = line.strip().lower()
        if len(clean_line) > 3:  # Ignorar líneas muy cortas
            line_counts[clean_line] = line_counts.get(clean_line, 0) + 1
    
    # Contar cuántas líneas aparecen más de una vez
    return sum(1 for count in line_counts.values() if count > 1)

def _detect_song_structure(lines: list) -> bool:
    """Detectar estructura repetitiva típica de canciones (ABAB, AABA, etc.)"""
    if len(lines) < 4:
        return False
    
    # Analizar patrones en grupos de 4 líneas
    for i in range(0, len(lines) - 3, 4):
        group = lines[i:i+4]
        group_lower = [line.lower().strip() for line in group]
        
        # Patrón ABAB
        if group_lower[0] == group_lower[2] or group_lower[1] == group_lower[3]:
            return True
        
        # Patrón AABA
        if group_lower[0] == group_lower[1] == group_lower[3]:
            return True
    
    return False

def _analyze_word_repetition(text_lower: str) -> int:
    """Analizar repetición de palabras significativas"""
    words = text_lower.split()
    word_counts = {}
    
    # Filtrar palabras comunes que no son significativas
    stop_words = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'una', 'del', 'los', 'las', 'al', 'mi', 'tu'}
    
    for word in words:
        # Limpiar puntuación
        clean_word = re.sub(r'[^\w]', '', word)
        if len(clean_word) > 3 and clean_word not in stop_words:
            word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
    
    # Contar palabras que aparecen 3 o más veces
    return sum(1 for count in word_counts.values() if count >= 3)

def _detect_strong_rhyme_pattern(lines: list) -> bool:
    """Detectar patrones de rima más fuertes"""
    if len(lines) < 2:
        return False
    
    endings = []
    for line in lines:
        words = line.split()
        if words:
            last_word = words[-1].lower()
            # Quitar puntuación
            last_word = re.sub(r'[^\w]', '', last_word)
            if len(last_word) >= 3:
                # Tomar las últimas 2-3 letras
                endings.append(last_word[-3:])
    
    if len(endings) < 2:
        return False
    
    # Buscar patrones de rima más complejos
    rhyme_patterns = 0
    
    # Verificar rimas ABAB, AABB, etc.
    for i in range(len(endings)):
        for j in range(i + 1, len(endings)):
            if endings[i] == endings[j]:
                rhyme_patterns += 1
    
    # Más de 2 rimas sugiere patrón fuerte
    return rhyme_patterns >= 2

def _detect_verse_chorus_structure(lines: list) -> bool:
    """Detectar estructura verso-estribillo"""
    if len(lines) < 6:
        return False
    
    # Buscar bloques de líneas repetidas que podrían ser estribillos
    line_positions = {}
    for i, line in enumerate(lines):
        clean_line = line.strip().lower()
        if len(clean_line) > 5:  # Ignorar líneas muy cortas
            if clean_line not in line_positions:
                line_positions[clean_line] = []
            line_positions[clean_line].append(i)
    
    # Buscar líneas que aparecen en posiciones que sugieren estructura verso-estribillo
    for line, positions in line_positions.items():
        if len(positions) >= 2:
            # Si hay líneas repetidas separadas por algunas líneas, podría ser estribillo
            gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            # Estribillos suelen repetirse cada 4-8 líneas
            if any(3 <= gap <= 8 for gap in gaps):
                return True
    
    return False