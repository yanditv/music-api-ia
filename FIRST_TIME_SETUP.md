# 🚀 Configuración para Primera Vez

Esta guía explica exactamente qué esperar cuando ejecutas la API por primera vez.

## 📥 ¿Qué se descarga automáticamente?

La primera vez que hagas una petición a `/generate/`, se descargarán estos modelos:

### Modelos de Bark (Total: ~6.6GB)

```
📦 suno/bark_v0/
├── text_2.pt      (~1.2GB) - Modelo de procesamiento de texto
├── coarse_2.pt    (~2.4GB) - Modelo de audio grueso
└── fine_2.pt      (~3.0GB) - Modelo de audio fino

📦 bert-base-multilingual-cased/
├── pytorch_model.bin  (~650MB) - Modelo BERT
├── tokenizer.json     (~15MB)  - Tokenizador
├── vocab.txt         (~996KB)  - Vocabulario
└── config.json       (~1KB)   - Configuración
```

### Ubicación de archivos

```
app/models/
├── transformers/           # Modelos de Hugging Face Transformers
│   └── models--bert-base-multilingual-cased/
├── cache/suno/bark_v0/     # Modelos principales de Bark
│   ├── text_2.pt
│   ├── coarse_2.pt
│   └── fine_2.pt
├── torch/hub/              # Cache de PyTorch
└── huggingface/            # Cache general de HF
```

## ⏱️ Tiempos esperados

### Primera ejecución completa:

1. **Iniciar servidor**: 1-2 minutos 🐌
   - 📥 Descarga modelos: 30-90 segundos (si es primera vez)
   - 🧠 Carga en memoria: 10-15 segundos
   - ⚡ Servidor listo: inmediato
2. **Primera petición**: 2-5 segundos ⚡
   - 🎵 Genera audio: 2-5 segundos (modelos ya en memoria)

### Ejecuciones posteriores:

1. **Iniciar servidor**: 10-15 segundos 🚀
   - 🧠 Carga modelos en memoria: 10-15 segundos (ya descargados)
   - ⚡ Servidor listo: inmediato
2. **Todas las peticiones**: 2-5 segundos ⚡⚡

## 🖥️ Ejemplo paso a paso

### 1. Instalar dependencias (solo primera vez)

```bash
git clone <your-repo>
cd music-api-ia
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar servidor

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada (primera vez):**

```
🚀 Precargando modelos de Bark al iniciar la API...
⏳ Si es la primera vez, esto descargará ~6.6GB de modelos...

Downloading (…)lve/main/config.json: 100%|██████████| 570/570 [00:00<00:00, 123kB/s]
Downloading (…)main/pytorch_model.bin: 100%|██████████| 625M/625M [01:23<00:00, 7.50MB/s]
Downloading (…)okenizer_config.json: 100%|██████████| 25.0k/25.0k [00:00<00:00, 456kB/s]
Downloading (…)solve/main/vocab.txt: 100%|██████████| 996k/996k [00:00<00:00, 1.20MB/s]
Downloading (…)/main/tokenizer.json: 100%|██████████| 15.6M/15.6M [00:02<00:00, 6.50MB/s]

Downloading text_2.pt: 100%|██████████| 1.21G/1.21G [02:15<00:00, 8.95MB/s]
Downloading coarse_2.pt: 100%|██████████| 2.42G/2.42G [04:32<00:00, 8.88MB/s]
Downloading fine_2.pt: 100%|██████████| 3.01G/3.01G [05:41<00:00, 8.82MB/s]

✅ Modelos cargados correctamente y listos para usar!
📁 Cache de modelos configurado en: /path/to/app/models

INFO:     Will watch for changes in these directories: ['/path/to/music-api-ia']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Salida esperada (siguientes veces):**

```
🚀 Precargando modelos de Bark al iniciar la API...
⏳ Si es la primera vez, esto descargará ~6.6GB de modelos...
✅ Modelos cargados correctamente y listos para usar!
📁 Cache de modelos configurado en: /path/to/app/models

INFO:     Will watch for changes in these directories: ['/path/to/music-api-ia']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Primera petición (RÁPIDA - los modelos ya están cargados!)

```bash
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world, this is my first test", "voice": "v2/en_speaker_6"}' \
  --output first_audio.wav
```

**Salida en terminal del servidor:**

```
🎵 Generando audio para: 'Hello world, this is my first test' con voz: v2/en_speaker_6
Audio guardado en: generated_audio/abc123-def456.wav
```

### 4. Segunda petición (También RÁPIDA!)

```bash
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "This second request will be much faster!", "voice": "v2/en_speaker_3"}' \
  --output second_audio.wav
```

**Salida en terminal:**

```
🎵 Generando audio para: 'This second request will be much faster!' con voz: v2/en_speaker_3
Audio guardado en: generated_audio/xyz789-abc123.wav
```

## 💾 Uso de espacio en disco

Después de la primera ejecución:

```
du -sh app/models/
6.6G    app/models/
```

**Desglose:**

- `cache/suno/bark_v0/`: ~6.6GB (modelos principales)
- `transformers/`: ~650MB (BERT)
- `torch/`: ~50MB (cache)
- `huggingface/`: ~20MB (metadatos)

## 🧹 Limpiar cache (opcional)

Si quieres empezar de cero:

```bash
rm -rf app/models/
```

En la siguiente petición, se volverán a descargar todos los modelos.

## ✅ Verificar que todo funciona

### Test rápido después de la primera descarga:

```bash
# 1. Reiniciar servidor
# 2. Hacer petición de prueba
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing after restart", "voice": "v2/en_speaker_0"}' \
  --output test.wav

# Debería tomar solo 10-15 segundos (no hay descarga)
```

### Test de voces en español:

```bash
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, esta es una prueba en español", "voice": "v2/es_speaker_2"}' \
  --output spanish_test.wav
```

## 🆘 Si algo sale mal

### Error común: "No space left on device"

- **Causa**: No hay espacio para 6.6GB
- **Solución**: Liberar espacio en disco

### Error: "Connection timeout"

- **Causa**: Descarga lenta de modelos
- **Solución**: Esperar más tiempo o mejorar conexión

### Error: "CUDA out of memory"

- **Causa**: GPU con poca memoria
- **Solución**: Se usará CPU automáticamente (más lento pero funciona)

---

**🎉 ¡Una vez completada la primera descarga, la API será muy rápida!**
