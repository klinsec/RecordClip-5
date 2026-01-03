🎥 RecordClip Studio Pro
RecordClip Studio Pro es una suite de grabación de alto rendimiento diseñada para creadores de contenido y gamers. Utiliza una arquitectura híbrida única: combina la potencia bruta de FFmpeg para el vídeo (acelerado por GPU) con la precisión de Python (SoundCard/NumPy) para el procesamiento de audio multipista en alta fidelidad.

A diferencia de otros grabadores, RecordClip está optimizado para Replay Buffer (ShadowPlay) y grabación de audio 32-bit Float, permitiendo una edición en cámara lenta (slow-motion) sin distorsión robótica.

✨ Características Principales
🎬 Vídeo de Alto Rendimiento
Motor FFmpeg Nativo: Integración directa con ddagrab (Desktop Duplication API) para una captura con latencia cero.

Soporte NVENC (NVIDIA): Configurado con presets P1 (Ultra Performance) y ULL (Ultra Low Latency).

Altos FPS: Soporte probado para grabaciones de hasta 240 FPS estables.

Buffer en RAM: Grabación cíclica en memoria RAM (sin desgaste de SSD) para guardar los últimos "X" segundos de juego (Replay).

🎙️ Audio de Estudio (Ultra-High Fidelity)
32-bit Float Audio: Grabación en rango dinámico infinito. Imposible de saturar (clipping) y perfecto para post-producción.

Alta Frecuencia de Muestreo: Soporte nativo para 48kHz y experimental para 96kHz, ideal para ralentizar el audio sin pérdida de calidad.

Pistas Independientes: Graba tu micrófono, el juego y Discord en pistas separadas dentro del mismo archivo MKV.

Búfer Masivo: Sistema de búfer de 8192 muestras para eliminar cualquier artefacto robótico o glitch sonoro.

🎨 Interfaz Moderna
UI Profesional: Interfaz construida en PyQt6 con diseño de tarjetas.

Temas Dinámicos: Cambio instantáneo entre Modo Oscuro (Dark Slate) y Modo Claro.

Perfiles: Guarda y carga configuraciones para distintos juegos o situaciones.

Atajos Globales: Controla la grabación y el guardado de clips con el teclado (F9, F10, etc.) aunque la app esté minimizada.

🛠️ Instalación
1. Requisitos Previos
Python 3.10 o superior.

Tarjeta Gráfica NVIDIA (Recomendada para el modo NVENC).

Windows 10/11.

2. Clonar el Repositorio
Bash

git clone https://github.com/tu-usuario/RecordClip-Studio.git
cd RecordClip-Studio
3. Instalar Dependencias
Es CRÍTICO instalar las versiones correctas para evitar conflictos de audio con NumPy 2.0. Ejecuta el script automático:

Opción A (Automática): Ejecuta el archivo install.bat.

Opción B (Manual):

Bash

pip install PyQt6 pynput
pip install "numpy<2.0" soundcard soundfile --force-reinstall
4. Configurar FFmpeg
El programa requiere una versión Full Build de FFmpeg (con soporte de librerías compartidas).

Descarga FFmpeg (versión ffmpeg-git-full.7z recomendada) desde Gyan.dev.

Extrae el archivo ffmpeg.exe de la carpeta bin.

Coloca ffmpeg.exe dentro de la carpeta raíz del proyecto (junto a main_ui.py).

🚀 Uso
Ejecuta el programa con doble clic en run.bat o desde la terminal:

Bash

python main_ui.py
Selecciona tu Perfil: Crea uno nuevo o usa el "Default".

Configura el Audio:

Haz clic en "Añadir Pista".

Selecciona tu Micrófono y/o la Salida de Sistema (Speakers).

Elige el Modo:

🔴 Grabar: Grabación tradicional continua.

⚡ Buffer: Mantiene los últimos segundos en RAM. Pulsa "Guardar Clip" (o el atajo) para volcarlo a disco.

⚙️ Arquitectura Técnica
RecordClip Studio funciona mediante un sistema de Multiprocesamiento y Hilos:

Core de Vídeo: Un subproceso de subprocess maneja FFmpeg, enviando datos crudos de vídeo a un deque (cola) en memoria RAM si se usa el modo Buffer.

Workers de Audio: Cada pista de audio seleccionada genera un threading.Thread independiente en Python. Estos hilos capturan audio usando soundcard en formato float32 y lo sincronizan manualmente.

Muxing Final: Al detener la grabación o guardar un clip, el sistema invoca una segunda instancia de FFmpeg para "coser" (mux) el vídeo y los archivos de audio WAV temporales en un contenedor final MKV/MP4 sin recodificación (-c copy), garantizando velocidad instantánea.

⚠️ Solución de Problemas Comunes
Error "ModuleNotFoundError: audio_manager": Asegúrate de ejecutar el script desde la carpeta raíz.

Audio Robótico: Aumenta el tamaño del búfer en el código o asegúrate de no estar forzando 96kHz en un dispositivo que solo soporta 44.1kHz.

Error de NumPy: Si el programa se cierra al iniciar, ejecuta pip install "numpy<2.0" --force-reinstall.

📄 Licencia
Este proyecto es de código abierto bajo la licencia MIT. Eres libre de modificarlo, mejorarlo y distribuirlo.

Desarrollado con ❤️ y mucho café.
