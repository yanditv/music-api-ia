import os
import numpy as np
import torch
from pathlib import Path
from functools import wraps

# PARCHE COMPLETO PARA PYTORCH 2.6+ - Debe ejecutarse antes de importar bark
def patch_torch_load():
    """Parche para PyTorch 2.6+ que fuerza weights_only=False y agrega safe_globals"""
    original_load = torch.load
    
    @wraps(original_load)
    def patched_load(*args, **kwargs):
        # Forzar weights_only=False para modelos de Bark
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    
    # Aplicar el parche
    torch.load = patched_load
    
    # Agregar safe_globals para numpy (más completo)
    try:
        torch.serialization.add_safe_globals([
            np.core.multiarray.scalar,
            np.core.multiarray._reconstruct, 
            np.core.multiarray.ndarray,
            np.dtype,
            np.ndarray,
            np.int64,
            np.float32,
            np.float64,
            getattr(np.core.multiarray, '_scalar', None),
        ])
        print("✅ Parche PyTorch 2.6+ aplicado: weights_only=False + safe_globals para numpy")
    except Exception as e:
        print(f"⚠️ Warning aplicando safe_globals: {e}")

# Aplicar parche inmediatamente
patch_torch_load()

from bark import SAMPLE_RATE, generate_audio as bark_generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

# Configurar cache local de modelos antes de cargar Bark
def setup_model_cache():
    """Configurar cache local para modelos de Bark"""
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    cache_vars = {
        'TRANSFORMERS_CACHE': str(models_dir / 'transformers'),
        'HF_HOME': str(models_dir / 'huggingface'), 
        'TORCH_HOME': str(models_dir / 'torch'),
        'XDG_CACHE_HOME': str(models_dir / 'cache'),
    }
    
    for var, path in cache_vars.items():
        os.environ[var] = path
        os.makedirs(path, exist_ok=True)
    
    print(f"📁 Cache de modelos configurado en: {models_dir}")
    return models_dir

# Configurar cache antes de importar/cargar modelos
setup_model_cache()

# Precargar modelos automáticamente al iniciar la aplicación
print("🚀 Precargando modelos de Bark al iniciar la API...")
print("⏳ Si es la primera vez, esto descargará ~6.6GB de modelos...")
preload_models()
print("✅ Modelos cargados correctamente y listos para usar!")

# Variable global para saber si los modelos ya están cargados
_models_loaded = True

def ensure_models_loaded():
    """Los modelos ya están cargados al iniciar la aplicación"""
    # Los modelos se precargan automáticamente al importar este módulo
    pass

def generate_audio(text: str, voice: str = "v2/en_speaker_6", output_file: str = "output.wav"):
    """
    Genera audio usando Bark
    
    Args:
        text: Texto a convertir en audio
        voice: Preset de voz (ej: "v2/en_speaker_6", "v2/es_speaker_0", etc.)
        output_file: Nombre del archivo de salida
    
    Returns:
        str: Ruta del archivo generado
    """
    try:
        # Asegurar que los modelos están cargados (solo una vez)
        ensure_models_loaded()
        
        print(f"🎵 Generando audio para: '{text[:50]}...' con voz: {voice}")
        
        # Generar audio con Bark (los modelos ya están en memoria)
        audio_array = bark_generate_audio(text, history_prompt=voice)
        
        # Asegurarse de que el audio esté en el formato correcto
        audio_array = np.array(audio_array)
        
        # Normalizar audio para evitar clipping
        audio_array = audio_array / np.max(np.abs(audio_array))
        
        # Convertir a int16 para WAV
        audio_array = (audio_array * 32767).astype(np.int16)
        
        # Guardar archivo WAV
        write_wav(output_file, SAMPLE_RATE, audio_array)
        
        print(f"Audio guardado en: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error generando audio: {str(e)}")
        raise e