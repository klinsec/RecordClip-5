import soundcard as sc
import soundfile as sf
import numpy as np

# Cache para no buscar dispositivos mil veces por segundo
_CACHED_MICS = []

def get_audio_devices():
    """
    Usa la librería 'soundcard' para detectar micrófonos y loopbacks (audio PC).
    Basado en la lógica de 'grabadora.py'.
    """
    global _CACHED_MICS
    devices = []
    
    try:
        # include_loopback=True es la clave para grabar el audio del sistema (Speakers)
        # Esto obtiene TODOS los dispositivos disponibles
        mics = sc.all_microphones(include_loopback=True)
        _CACHED_MICS = mics # Guardamos la referencia a los objetos reales
        
        for i, mic in enumerate(mics):
            try:
                nombre = mic.name
                # Determinamos el tipo basándonos en el nombre, igual que en tu script
                tipo = "input" # Por defecto input (micro)
                
                # Heurística para detectar si es Audio de Sistema (Loopback)
                # Si dice "Speakers", "Headset", "Sonar", "Stereo Mix" o "Mezcla" suele ser salida
                n_low = nombre.lower()
                if any(x in n_low for x in ["speakers", "headset", "sonar", "stereo", "mezcla", "altavoces", "auriculares"]):
                    tipo = "output" # Lo marcamos como output (PC/JUEGO) para la UI
                
                devices.append({
                    'index': i,          # Índice en la lista de soundcard
                    'name': nombre,      # Nombre legible
                    'type': tipo,        # Para ponerle el icono correcto en la UI
                    'id': nombre         # Usamos el nombre como ID persistente
                })
            except:
                continue
                
    except Exception as e:
        print(f"[AudioManager] Error detectando dispositivos: {e}")
        
    return devices

def get_mic_object_by_index(index):
    """Recupera el objeto 'mic' real de soundcard usando el índice."""
    global _CACHED_MICS
    if 0 <= index < len(_CACHED_MICS):
        return _CACHED_MICS[index]
    
    # Si por lo que sea no está en caché, refrescamos
    mics = sc.all_microphones(include_loopback=True)
    _CACHED_MICS = mics
    if 0 <= index < len(mics):
        return mics[index]
    return None

if __name__ == "__main__":
    # Test rápido (igual que tu script original)
    print("--- Test Audio Manager (SoundCard) ---")
    devs = get_audio_devices()
    for d in devs:
        print(f"[{d['index']}] {d['type'].upper()}: {d['name']}")