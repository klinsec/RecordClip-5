🎥 RecordClip 5
RecordClip 5 es una herramienta de grabación de alto rendimiento diseñada para capturar tus mejores momentos de juego sin sacrificar FPS. Utiliza una arquitectura híbrida única: vídeo acelerado por hardware (FFmpeg/NVENC) y audio de alta fidelidad (32-bit Float) mediante Python.

Diseñado para ser ligero, potente y con Replay Buffer (grabación en RAM) incluido.

🚀 Instalación Rápida
Solo necesitas 3 pasos para empezar:

1. Instalar Python
Asegúrate de tener instalado Python 3.10 o superior.

Importante: Marca la casilla "Add Python to PATH" durante la instalación.

2. Colocar FFmpeg
Descarga la versión Full Build de FFmpeg (Gyan.dev).

Abre el archivo descargado, entra en la carpeta bin.

Extrae el archivo ffmpeg.exe y pégalo dentro de esta misma carpeta (junto a main_ui.py).

3. Ejecutar el Instalador
Haz doble clic en el archivo install.bat.

Esto instalará automáticamente todas las librerías necesarias.

Aplicará el parche de compatibilidad para el audio (NumPy < 2.0).

🎮 Cómo Usar
Una vez instalado, tienes dos formas de abrir el programa:

Opción Recomendada: Ejecuta run.vbs.

Esto abrirá el programa de forma silenciosa (sin la ventana negra de comandos de fondo).

Opción Debug: Ejecuta run.bat.

Útil si tienes problemas y necesitas ver los mensajes de error en la consola.

Características
Configuración de Vídeo: Soporte para NVENC (NVIDIA), altos FPS (hasta 240fps) y bitrate ajustable.

Audio Multipista: Graba tu micrófono y el sonido del juego/Discord en pistas separadas.

Modo Buffer: Mantén los últimos segundos en la memoria RAM y guárdalos solo cuando ocurra algo épico.

Perfiles: Guarda tus configuraciones favoritas.

📁 Estructura de Archivos
main_ui.py: La interfaz gráfica principal.

recorder_core.py: El motor de grabación (vídeo + audio sync).

audio_manager.py: Sistema de detección de dispositivos de audio.

profile_manager.py: Gestor de perfiles y configuraciones JSON.

install.bat: Script de instalación automática de dependencias.

run.vbs: Lanzador silencioso.

⚠️ Solución de Problemas
¿El programa se cierra al abrir? Asegúrate de haber ejecutado install.bat al menos una vez para corregir las versiones de las librerías de audio.

¿No detecta el audio? Verifica que tus dispositivos de sonido no estén desconectados. El programa filtrará automáticamente los dispositivos disponibles.

¿Error de FFmpeg? Asegúrate de que el archivo ffmpeg.exe está en la misma carpeta que el script.
Desarrollado con ❤️ y mucho café.
