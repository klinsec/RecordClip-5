import subprocess
import os
import shutil
import time
import threading
import collections
import sys
import numpy as np
import soundfile as sf
from pathlib import Path

# Importamos el manager de audio
import audio_manager 

class AudioWorker(threading.Thread):
    """
    Hilo de grabación de audio de ALTA FIDELIDAD (32-bit float).
    """
    def __init__(self, device_index, device_name, filename, is_buffer_mode=False, buffer_duration=30):
        super().__init__()
        self.device_index = device_index
        self.device_name = device_name
        self.filename = filename
        self.running = True
        self.is_buffer_mode = is_buffer_mode
        
        # 48kHz es el estándar nativo para evitar glitches robóticos
        self.samplerate = 48000 
        self.block_size = 4096 
        self.subtype = 'FLOAT' 
        
        # Lock para evitar errores si leemos el buffer mientras se escribe
        self.lock = threading.Lock()
        
        # --- BÚFER MASIVO ---
        # Multiplicamos por 5.0 la duración para que SOBRE audio.
        # Luego el sistema recortará el exceso, pero así aseguramos que nunca falte.
        safety_multiplier = 5.0
        
        maxlen = int((self.samplerate * (buffer_duration * safety_multiplier)) / self.block_size)
        self.ram_buffer = collections.deque(maxlen=maxlen)
        self.error = None

    def run(self):
        try:
            mic = audio_manager.get_mic_object_by_index(self.device_index)
            if not mic: return

            if not self.is_buffer_mode:
                # MODO GRABACIÓN
                with sf.SoundFile(self.filename, mode='w', samplerate=self.samplerate, channels=2, subtype=self.subtype) as file:
                    with mic.recorder(samplerate=self.samplerate, blocksize=self.block_size) as recorder:
                        while self.running:
                            data = recorder.record(numframes=self.block_size)
                            file.write(data)
            else:
                # MODO BUFFER
                with mic.recorder(samplerate=self.samplerate, blocksize=self.block_size) as recorder:
                    while self.running:
                        data = recorder.record(numframes=self.block_size)
                        # Protegemos la escritura en RAM
                        with self.lock:
                            self.ram_buffer.append(data)
                        
        except Exception as e:
            self.error = e
            print(f"[AUDIO-THREAD] Error grabando {self.device_name}: {e}")

    def stop(self):
        self.running = False
    
    def get_snapshot(self):
        """
        Devuelve una COPIA instantánea de lo que hay en RAM.
        Esto se hace antes de escribir a disco para asegurar sincronía perfecta.
        """
        with self.lock:
            if not self.ram_buffer: return None
            try:
                return np.concatenate(self.ram_buffer)
            except: return None

    def save_snapshot_to_file(self, audio_data):
        """Escribe los datos capturados a disco"""
        if audio_data is None: return False
        try:
            sf.write(self.filename, audio_data, self.samplerate, subtype=self.subtype)
            return True
        except Exception as e:
            print(f"[AUDIO-THREAD] Error guardando wav: {e}")
            return False


class RecorderCore:
    def __init__(self):
        self.process = None
        self.is_recording = False
        self.is_replay_active = False
        
        self.ffmpeg_exec = self._detect_ffmpeg_executable()
        print(f"[CORE] Motor de video: {self.ffmpeg_exec}")
        
        self.video_ram_buffer = collections.deque()
        self.video_ram_lock = threading.Lock()
        self.video_thread = None
        
        self.audio_workers = []
        
        self.temp_dir = Path(os.getcwd()) / "Temp_Processing"
        self.recordings_dir = Path(os.getcwd()) / "Recordings"
        
        self.settings = {
            "fps": 60,
            "resolution": "1920x1080",
            "bitrate": "6000k",
            "codec": "h264_nvenc",
            "container": "mkv",
            "save_path": str(self.recordings_dir),
            "replay_time": 30,
            "capture_mode": "ddagrab",
            "monitor_idx": 0,
            "audio_tracks": []
        }

    def _detect_ffmpeg_executable(self):
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(base_dir, "ffmpeg.exe")
        return local_ffmpeg if os.path.exists(local_ffmpeg) else "ffmpeg"

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        if not os.path.exists(self.settings["save_path"]):
            os.makedirs(self.settings["save_path"])
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True)

    def _get_video_cmd(self, output_target, is_buffer_mode=False):
        fps = str(self.settings["fps"])
        bitrate = self.settings["bitrate"]
        codec = self.settings["codec"]
        capture_mode = self.settings.get("capture_mode", "ddagrab")
        monitor_idx = self.settings.get("monitor_idx", 0)
        using_nvenc = "nvenc" in codec

        cmd = [
            self.ffmpeg_exec, "-y", "-hide_banner", 
            "-thread_queue_size", "9192", 
            "-rtbufsize", "2048M"
        ]
        
        if "ddagrab" in capture_mode and using_nvenc:
            cmd.extend(["-init_hw_device", "d3d11va=gpu:0", "-filter_hw_device", "gpu"])
            cmd.extend(["-extra_hw_frames", "256"]) 
            cmd.extend([
                "-f", "lavfi",
                "-i", f"ddagrab=framerate={fps}:draw_mouse=0:output_idx={monitor_idx}"
            ])
        elif "ddagrab" in capture_mode:
            cmd.extend([
                "-f", "lavfi",
                "-i", f"ddagrab=framerate={fps}:draw_mouse=0:output_idx={monitor_idx}",
                "-vf", "hwdownload,format=nv12"
            ])
        else:
            cmd.extend(["-f", "gdigrab", "-framerate", fps, "-i", "desktop"])

        cmd.extend(["-c:v", codec])
        bitrate_val = int(bitrate[:-1])
        cmd.extend(["-b:v", bitrate, "-maxrate", bitrate, "-bufsize", str(bitrate_val * 4)+"k"])
        
        if using_nvenc:
            fps_val = int(self.settings["fps"])
            cmd.extend(["-fps_mode", "cfr"]) 
            if fps_val >= 120:
                cmd.extend([
                    "-preset", "p1", "-tune", "ull", "-rc", "cbr",         
                    "-zerolatency", "1", "-bf", "0"            
                ])
            else:
                cmd.extend(["-preset", "p4", "-rc", "cbr"])
            cmd.extend(["-g", str(fps_val)]) 
        else:
            cmd.extend(["-preset", "ultrafast"])

        if is_buffer_mode:
            cmd.extend(["-f", "mpegts", "-muxdelay", "0.1", "-"])
        else:
            cmd.append(output_target)
            
        return cmd

    # ==========================================================
    #  BUFFER
    # ==========================================================
    def start_replay_buffer(self):
        if self.is_replay_active: return
        self.video_ram_buffer.clear()
        
        cmd = self._get_video_cmd(None, is_buffer_mode=True)
        print("[BUFFER] Video RAM Iniciado...")
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=128*1024*1024)
        
        self.is_replay_active = True
        self.video_thread = threading.Thread(target=self._video_buffer_worker)
        self.video_thread.start()
        
        self.audio_workers = []
        for i, track in enumerate(self.settings.get("audio_tracks", [])):
            worker = AudioWorker(track['index'], track['name'], None, True, self.settings["replay_time"])
            worker.start()
            self.audio_workers.append(worker)

    def _video_buffer_worker(self):
        bitrate_k = int(self.settings["bitrate"].replace('k', ''))
        bytes_per_sec = (bitrate_k * 1000) / 8
        # Reducimos el multiplicador de seguridad del video para que no se pase tanto de tiempo
        max_buffer_size = int(bytes_per_sec * self.settings["replay_time"] * 1.3)
        
        chunk = 8 * 1024 * 1024 
        current_size = 0
        try:
            while self.is_replay_active and self.process:
                data = self.process.stdout.read(chunk)
                if not data: break
                with self.video_ram_lock:
                    self.video_ram_buffer.append(data)
                    current_size += len(data)
                    while current_size > max_buffer_size and self.video_ram_buffer:
                        removed = self.video_ram_buffer.popleft()
                        current_size -= len(removed)
        except: pass

    # ==========================================================
    #  GRABACIÓN DIRECTA
    # ==========================================================
    def start_recording(self):
        if self.is_recording: return
        timestamp = int(time.time())
        self.temp_video_path = self.temp_dir / f"temp_vid_{timestamp}.mkv"
        self.final_output_path = Path(self.settings["save_path"]) / f"Recording_{timestamp}.{self.settings['container']}"
        
        cmd = self._get_video_cmd(str(self.temp_video_path), is_buffer_mode=False)
        print(f"[REC] Grabando...")
        self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        
        self.audio_workers = []
        for i, track in enumerate(self.settings.get("audio_tracks", [])):
            wav_filename = self.temp_dir / f"temp_audio_{timestamp}_{i}.wav"
            worker = AudioWorker(track['index'], track['name'], str(wav_filename), False)
            worker.start()
            self.audio_workers.append(worker)
        self.is_recording = True

    def stop_recording(self):
        if not self.is_recording: return
        self._stop_ffmpeg()
        for worker in self.audio_workers:
            worker.stop()
            worker.join()
        self.is_recording = False
        # En modo normal no usamos recorte, guardamos todo
        self._mux_files(self.temp_video_path, self.audio_workers, self.final_output_path, trim_duration=None)

    # ==========================================================
    #  GUARDADO INTELIGENTE (SNAPSHOT + TRIM)
    # ==========================================================
    def save_replay(self):
        if not self.is_replay_active: return
        print("[SAVE] Iniciando guardado sincronizado...")
        timestamp = int(time.time())
        
        # 1. CAPTURA INSTANTÁNEA (Evita desfase Video vs Audio)
        # Capturamos el audio de la RAM *antes* de ponernos a escribir el video (que es lento)
        audio_snapshots = []
        for worker in self.audio_workers:
            audio_snapshots.append(worker.get_snapshot())
            
        # 2. Escribir Video RAM -> Disco
        ts_filename = self.temp_dir / f"temp_replay_vid_{timestamp}.ts"
        try:
            with open(ts_filename, "wb") as f:
                with self.video_ram_lock:
                    for chunk in self.video_ram_buffer:
                        f.write(chunk)
        except: return

        # 3. Escribir Audio RAM (Snapshot) -> Disco
        wav_files_workers = []
        for i, worker in enumerate(self.audio_workers):
            wav_path = self.temp_dir / f"temp_replay_aud_{timestamp}_{i}.wav"
            worker.filename = str(wav_path)
            # Guardamos lo que capturamos en el paso 1
            if worker.save_snapshot_to_file(audio_snapshots[i]):
                wav_files_workers.append(worker)
        
        final_path = Path(self.settings["save_path"]) / f"Replay_{timestamp}.{self.settings['container']}"
        
        # 4. UNIR Y RECORTAR EXACTAMENTE AL TIEMPO PEDIDO
        # Pasamos replay_time para que FFmpeg corte lo que sobre
        self._mux_files(ts_filename, wav_files_workers, final_path, trim_duration=self.settings["replay_time"])
        
        try: os.remove(ts_filename)
        except: pass

    def stop_replay_buffer(self):
        self.is_replay_active = False
        self._stop_ffmpeg()
        if self.video_thread: self.video_thread.join()
        for worker in self.audio_workers:
            worker.stop()
            worker.join()
        self.video_ram_buffer.clear()

    def _stop_ffmpeg(self):
        if self.process:
            try:
                self.process.stdin.write(b'q')
                self.process.stdin.flush()
                self.process.wait(timeout=2)
            except:
                try: self.process.kill()
                except: pass
            self.process = None

    def _mux_files(self, video_path, audio_workers_list, final_path, trim_duration=None):
        print(f"[MUX] Generando: {final_path}")
        cmd = [self.ffmpeg_exec, "-y", "-hide_banner"]
        
        # --- TRUCO MAGICO: -sseof ---
        # Si trim_duration es 60, le decimos a FFmpeg:
        # "Ve al final del archivo y retrocede 60 segundos. Empieza a copiar desde ahí".
        # Esto elimina el exceso del principio y garantiza duración exacta.
        seek_cmd = []
        if trim_duration:
            seek_cmd = ["-sseof", f"-{trim_duration}"]
        
        # Input Video (con recorte si aplica)
        cmd.extend(seek_cmd) 
        cmd.extend(["-i", str(video_path)])
        
        valid_audios = []
        for worker in audio_workers_list:
            if os.path.exists(worker.filename):
                # Input Audio (con el mismo recorte para que vayan a la par)
                cmd.extend(seek_cmd) 
                cmd.extend(["-i", worker.filename])
                valid_audios.append(worker)
        
        cmd.extend(["-map", "0:v"])
        is_mkv = str(final_path).lower().endswith(".mkv")
        
        for i, worker in enumerate(valid_audios):
            cmd.extend(["-map", f"{i+1}:a"])
            if is_mkv:
                cmd.extend([f"-c:a:{i}", "pcm_f32le", f"-metadata:s:a:{i}", f"title={worker.device_name}"])
            else:
                cmd.extend([f"-c:a:{i}", "aac", f"-b:a:{i}", "320k", f"-metadata:s:a:{i}", f"title={worker.device_name}"])
        
        cmd.extend(["-c:v", "copy"])
        if not is_mkv: cmd.extend(["-bsf:a", "aac_adtstoasc"])
            
        cmd.append(str(final_path))
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        try:
            if os.path.exists(video_path): os.remove(video_path)
            for worker in valid_audios:
                if os.path.exists(worker.filename): os.remove(worker.filename)
        except: pass