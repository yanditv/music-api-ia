# Bark Text-to-Speech API

Una API REST para síntesis de voz usando el modelo Bark de Suno AI, optimizada para PyTorch 2.6+ con cache local persistente.

## 🚀 Características

- **API REST completa** con FastAPI
- **Compatible con PyTorch 2.6+** (parche automático)
- **Cache local persistente** (modelos se descargan una sola vez)
- **Carga bajo demanda** (modelos se cargan solo cuando se necesitan)
- **Múltiples voces** (inglés, español y otros idiomas)
- **Audio de calidad** (WAV 16-bit, 24kHz)

## 📋 Requisitos

- Python 3.9+
- ~6.6GB de espacio libre (para modelos)
- ~3GB RAM (cuando modelos están cargados)

## 🛠️ Instalación

1. **Clonar el repositorio**:

```bash
git clone <repo-url>
cd music-api-ia
```

2. **Crear entorno virtual**:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Uso

### Iniciar el servidor

**🚀 Forma más simple:**

```bash
python start.py
```

**🔧 Otras formas:**

```bash
# Usando el módulo app
python -m app

# Usando Make (si disponible)
make start

# Comando tradicional de uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

### ⚠️ Primera Ejecución

**Importante**: La primera vez que uses la API:

1. **Los modelos se descargarán automáticamente al iniciar** (~6.6GB)
2. **El servidor tardará 1-2 minutos en estar listo** (descarga + carga)
3. **Una vez iniciado, todas las peticiones serán rápidas** (2-5 segundos)

**Ejemplo de primera ejecución**:

```bash
# 1. Iniciar servidor (LENTO - 1-2 minutos en primera vez)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# ⏳ Aquí se descargan y cargan todos los modelos automáticamente
# ✅ Cuando veas "Application startup complete", ya está listo

# 2. Primera petición (RÁPIDA - 2-5 segundos)
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola mundo", "voice": "v2/es_speaker_0"}' \
  --output audio.wav

# 3. Segunda petición (También RÁPIDA - 2-5 segundos)
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Esta también será rápida", "voice": "v2/es_speaker_1"}' \
  --output audio2.wav
```

**Lo que sucede internamente**:

- 📥 **Al iniciar**: Descarga modelos de Hugging Face → `app/models/`
- 🧠 **Al iniciar**: Carga modelos en memoria (~3GB RAM)
- ✅ **Servidor listo**: Todas las peticiones son inmediatas
- ⚡ **Siguientes inicios**: Solo carga modelos (ya descargados), ~10-15 segundos

### Documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🌐 Endpoints

### `GET /health`

Verificar el estado de la API

```bash
curl http://localhost:8000/health
```

### `GET /voices`

Obtener lista de voces disponibles

```bash
curl http://localhost:8000/voices
```

### `POST /generate/`

Generar audio desde texto

```bash
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola mundo", "voice": "v2/es_speaker_0"}' \
  --output audio.wav
```

**Parámetros**:

- `text` (string, requerido): Texto a convertir en audio
- `voice` (string, opcional): Voz a usar (por defecto: "v2/en_speaker_6")

## 🎭 Voces Disponibles

### Inglés

- `v2/en_speaker_0` a `v2/en_speaker_9`

### Español

- `v2/es_speaker_0` a `v2/es_speaker_9`

### Otros idiomas

- **Chino**: `v2/zh_speaker_0` a `v2/zh_speaker_2`
- **Francés**: `v2/fr_speaker_0` a `v2/fr_speaker_2`
- **Alemán**: `v2/de_speaker_0` a `v2/de_speaker_2`
- **Italiano**: `v2/it_speaker_0` a `v2/it_speaker_2`
- **Japonés**: `v2/ja_speaker_0` a `v2/ja_speaker_2`
- **Coreano**: `v2/ko_speaker_0` a `v2/ko_speaker_2`
- **Portugués**: `v2/pt_speaker_0` a `v2/pt_speaker_2`
- **Ruso**: `v2/ru_speaker_0` a `v2/ru_speaker_2`
- Y más...

## 💡 Ejemplos de Uso

### Python

```python
import requests

# Generar audio en español
response = requests.post("http://localhost:8000/generate/",
    json={
        "text": "¡Hola! Esta es una prueba de síntesis de voz en español.",
        "voice": "v2/es_speaker_2"
    })

if response.status_code == 200:
    with open("audio_español.wav", "wb") as f:
        f.write(response.content)
    print("Audio generado: audio_español.wav")
```

### JavaScript

```javascript
fetch("http://localhost:8000/generate/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    text: "Hello, this is a test of Bark text-to-speech.",
    voice: "v2/en_speaker_3",
  }),
})
  .then((response) => response.blob())
  .then((blob) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "audio.wav";
    a.click();
  });
```

## 🔧 Configuración Técnica

### Cache de Modelos

Los modelos se almacenan en `app/models/` y incluyen:

- `transformers/`: Modelos de transformers
- `huggingface/`: Cache de Hugging Face
- `torch/`: Modelos de PyTorch
- `cache/`: Cache general

### Variables de Entorno

Se configuran automáticamente:

- `TRANSFORMERS_CACHE`
- `HF_HOME`
- `TORCH_HOME`
- `XDG_CACHE_HOME`

### Parche PyTorch 2.6+

Se aplica automáticamente al importar `bark_utils`:

- Fuerza `weights_only=False` en `torch.load`
- Agrega `safe_globals` para numpy
- Compatible con numpy moderno y legacy

## 📁 Estructura del Proyecto

```
music-api-ia/
├── app/
│   ├── __init__.py
│   ├── main.py          # API FastAPI
│   ├── bark_utils.py    # Funciones de Bark + parche PyTorch
│   └── models/          # Cache local de modelos (auto-creado)
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Imagen Docker (opcional)
├── README.md           # Este archivo
└── STATUS.md          # Estado del proyecto
```

## 🐛 Solución de Problemas

### ⏱️ "El servidor tarda mucho en iniciar"

✅ **Completamente normal** - En la primera ejecución:

- Se descargan ~6.6GB de modelos
- Se cargan en memoria (~3GB RAM)
- Puede tardar 1-2 minutos

**Solución**: ¡Solo espera! Es una sola vez. Cuando veas "Application startup complete", ya está listo.

### 💾 "¿Dónde se guardan los modelos?"

Los modelos se almacenan localmente en:

```
app/models/
├── transformers/    # Modelos de texto
├── huggingface/     # Cache de HF
├── torch/          # Modelos PyTorch
└── cache/          # Cache general
```

Una vez descargados, **nunca se vuelven a descargar**.

### Error: "GLOBAL numpy.core.multiarray.scalar was not allowed"

✅ **Solucionado automáticamente** - El parche se aplica al importar la app.

### Error: "No module named 'bark'"

```bash
pip install git+https://github.com/suno-ai/bark.git
```

### Los modelos se descargan muy lento

- **Primera vez**: Es normal, son ~6.6GB
- **Siguientes**: Los modelos se cargan del cache local

### La API tarda mucho en responder

- **Primera vez que inicias**: Normal, está descargando y cargando modelos
- **Siguientes inicios**: ~10-15 segundos (carga modelos del cache)
- **Peticiones HTTP**: Deberían ser rápidas (~2-5 segundos)

## 📊 Rendimiento

- **Primera carga**: 10-15 segundos (descarga + carga)
- **Generación**: 2-5 segundos por frase
- **Memoria**: ~3GB cuando modelos están cargados
- **Almacenamiento**: ~6.6GB para todos los modelos

## 🚢 Deployment

### Docker (opcional)

```bash
docker build -t bark-api .
docker run -p 8000:8000 bark-api
```

### Producción

- Considerar usar `gunicorn` en lugar de `uvicorn`
- Configurar reverse proxy (nginx)
- Implementar rate limiting
- Monitoreo y logs

## 📝 Licencia

Este proyecto usa el modelo Bark de Suno AI. Consulta sus términos de uso.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**🎉 ¡Disfruta generando audio con Bark!**
