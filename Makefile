# Makefile para Bark Text-to-Speech API

.PHONY: start install test clean help

# Comando por defecto
help:
	@echo "🎵 Bark Text-to-Speech API - Comandos disponibles:"
	@echo ""
	@echo "  make start     - Iniciar el servidor de desarrollo"
	@echo "  make install   - Instalar dependencias"
	@echo "  make test      - Probar que la API funciona"
	@echo "  make clean     - Limpiar archivos temporales"
	@echo "  make help      - Mostrar esta ayuda"
	@echo ""

# Iniciar servidor
start:
	@echo "🚀 Iniciando Bark API..."
	python start.py

# Instalar dependencias
install:
	@echo "📦 Instalando dependencias..."
	pip install -r requirements.txt

# Probar la API
test:
	@echo "🧪 Probando la API..."
	python -c "from app.main import app; print('✅ API funciona correctamente')"

# Limpiar archivos temporales
clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf generated_audio/*.wav
	@echo "✅ Limpieza completada"
