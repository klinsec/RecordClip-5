import sys
import threading
import os
from pynput import keyboard
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QLineEdit, QFileDialog, QGroupBox, QSpinBox, 
                             QTextEdit, QInputDialog, QMessageBox, QGridLayout, QScrollArea, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QColor, QPalette

# Importamos los módulos del sistema
from recorder_core import RecorderCore
from profile_manager import ProfileManager
import audio_manager

# =============================================================================
#  SISTEMA DE TEMAS (DARK / LIGHT)
# =============================================================================

THEMES = {
    "dark": {
        "bg_app": "#121212",
        "bg_card": "#1E1E24",
        "text_main": "#E0E0E0",
        "text_dim": "#A0A0A0",
        "input_bg": "#2C2C35",
        "input_border": "#424242",
        "accent": "#2979FF",
        "border": "#333333",
        "scroll_bg": "#121212", 
        "scroll_handle": "#424242",
        "btn_normal": "#373740",
        "btn_hover": "#454555",
        "success": "#00E676",
        "danger": "#FF5252"
    },
    "light": {
        "bg_app": "#F4F6F8",
        "bg_card": "#FFFFFF",
        "text_main": "#212121",
        "text_dim": "#5F6368",
        "input_bg": "#F0F2F5",
        "input_border": "#D1D5DB",
        "accent": "#2962FF",
        "border": "#E0E0E0",
        "scroll_bg": "#F4F6F8",
        "scroll_handle": "#B0B0B0",
        "btn_normal": "#FFFFFF",
        "btn_hover": "#F5F5F5",
        "success": "#00C853",
        "danger": "#D32F2F"
    }
}

def get_stylesheet(theme_name):
    t = THEMES[theme_name]
    
    return f"""
    /* === FONDO PRINCIPAL === */
    QMainWindow, QWidget#central_widget {{
        background-color: {t['bg_app']};
        color: {t['text_main']};
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }}
    
    /* === SCROLL AREA (EL FIX DEL FONDO BLANCO) === */
    QScrollArea {{
        background-color: {t['bg_app']};
        border: none;
    }}
    QWidget#content_widget {{
        background-color: {t['bg_app']};
    }}
    
    /* === TARJETAS (GROUPS) === */
    QGroupBox {{
        background-color: {t['bg_card']};
        border: 1px solid {t['border']};
        border-radius: 10px;
        margin-top: 25px;
        padding-top: 25px;
        padding-bottom: 15px;
        padding-left: 20px;
        padding-right: 20px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 12px;
        background-color: {t['accent']};
        color: #FFFFFF;
        border-radius: 4px;
        margin-left: 15px;
        font-weight: bold;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* === INPUTS & COMBOS === */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {t['input_bg']};
        border: 1px solid {t['input_border']};
        border-radius: 6px;
        padding: 8px 10px;
        color: {t['text_main']};
        font-size: 14px;
        selection-background-color: {t['accent']};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {t['accent']};
    }}
    QComboBox::drop-down {{ border: 0px; width: 25px; }}
    
    /* === LABELS === */
    QLabel {{
        color: {t['text_dim']};
        font-weight: 500;
        background-color: transparent; /* Importante para que no coja fondo */
    }}
    QLabel#header_title {{
        color: {t['text_main']};
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 1px;
    }}
    
    /* === BOTONES STANDARD === */
    QPushButton {{
        background-color: {t['btn_normal']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        color: {t['text_main']};
        padding: 8px 15px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {t['btn_hover']};
        border: 1px solid {t['accent']};
    }}
    
    /* === BOTONES ACCIÓN (COLORES FIJOS PARA IMPACTO) === */
    QPushButton#btn_rec_start {{
        background-color: #D32F2F; color: white; border: none; font-size: 15px;
    }}
    QPushButton#btn_rec_start:hover {{ background-color: #B71C1C; }}
    
    QPushButton#btn_rec_stop {{
        background-color: transparent; border: 2px solid #D32F2F; color: #D32F2F; font-size: 15px; font-weight: bold;
    }}
    QPushButton#btn_rec_stop:hover {{ background-color: rgba(211, 47, 47, 0.1); }}

    QPushButton#btn_buff_start {{
        background-color: #388E3C; color: white; border: none; font-size: 15px;
    }}
    QPushButton#btn_buff_start:hover {{ background-color: #2E7D32; }}

    QPushButton#btn_buff_stop {{
        background-color: transparent; border: 2px solid #388E3C; color: #388E3C; font-size: 15px; font-weight: bold;
    }}

    QPushButton#btn_save_clip {{
        background-color: #FBC02D; color: #212121; border: none; font-size: 16px; font-weight: 800;
    }}
    QPushButton#btn_save_clip:hover {{ background-color: #F9A825; }}
    QPushButton#btn_save_clip:disabled {{ background-color: {t['input_bg']}; color: {t['text_dim']}; }}

    /* === SCROLLBAR === */
    QScrollBar:vertical {{
        border: none;
        background: {t['scroll_bg']};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {t['scroll_handle']};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

    /* === LOG AREA === */
    QTextEdit {{
        background-color: {t['bg_card']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        color: {t['success']};
        font-family: 'Consolas', monospace;
    }}
    """

# =============================================================================
#  CLASE PRINCIPAL
# =============================================================================

class WorkerSignals(QObject):
    log = pyqtSignal(str)
    update_rec_btn = pyqtSignal()
    update_buffer_btn = pyqtSignal()
    update_hotkey_ui = pyqtSignal(str, str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RecordClip Studio Pro")
        
        # --- DIMENSIONES MEJORADAS ---
        self.resize(750, 950) 
        
        # Estado del Tema
        self.current_theme = "dark" # dark o light

        # Backend
        self.recorder = RecorderCore()
        self.profiles = ProfileManager()
        
        # Variables
        self.audio_track_widgets = []
        self.cached_audio_devices = []
        self.hotkey_listener = None
        self.listening_for_new_hotkey = False
        self.hotkey_rec_str = '<f9>'
        self.hotkey_replay_str = '<f10>'

        # Signals
        self.signals = WorkerSignals()
        self.signals.log.connect(self.log_message)
        self.signals.update_rec_btn.connect(self.update_rec_button_state)
        self.signals.update_buffer_btn.connect(self.update_buffer_button_state)
        self.signals.update_hotkey_ui.connect(self.update_hotkey_display)

        # Build UI
        self.setup_ui()
        self.apply_theme() # Aplicar tema inicial
        
        # Inits
        self.detect_audio_devices_list()
        self.load_startup_profile()
        self.restart_hotkey_listener()

    def setup_ui(self):
        # Widget principal
        central_widget = QWidget()
        central_widget.setObjectName("central_widget") # ID para CSS
        self.setCentralWidget(central_widget)
        
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0) # Full width scroll
        
        # Scroll Area Profesional
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Contenedor del contenido (Aquí es donde forzamos el ID)
        content_widget = QWidget()
        content_widget.setObjectName("content_widget") # ID VITAL para el fondo oscuro
        
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(30, 30, 30, 30) # Breathing room
        
        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

        # === HEADER BAR (Título + Theme Switcher) ===
        header_layout = QHBoxLayout()
        
        title_col = QVBoxLayout()
        header_label = QLabel("RECORDCLIP STUDIO")
        header_label.setObjectName("header_title")
        subtitle_label = QLabel("Professional Recording Suite")
        subtitle_label.setStyleSheet("font-size: 13px; font-weight: normal; color: #888;")
        title_col.addWidget(header_label)
        title_col.addWidget(subtitle_label)
        title_col.setSpacing(0)
        
        # Botón Tema
        self.btn_theme = QPushButton("☀️") # Icono inicial
        self.btn_theme.setFixedSize(40, 40)
        self.btn_theme.setStyleSheet("border-radius: 20px; font-size: 18px;")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)

        header_layout.addLayout(title_col)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_theme)
        self.main_layout.addLayout(header_layout)

        # === 1. PERFILES (Tarjeta) ===
        prof_group = QGroupBox("Gestión de Perfiles")
        prof_layout = QHBoxLayout()
        prof_layout.setSpacing(10)
        
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumHeight(40)
        self.profile_combo.currentIndexChanged.connect(self.on_profile_changed)
        
        # Botones con iconos
        btn_save = QPushButton("💾 Guardar")
        btn_save.clicked.connect(self.save_current_profile)
        btn_new = QPushButton("➕ Nuevo")
        btn_new.clicked.connect(self.create_new_profile)
        btn_del = QPushButton("🗑️")
        btn_del.setFixedWidth(40)
        btn_del.setStyleSheet("color: #FF5252; border-color: rgba(255,82,82,0.5);")
        btn_del.clicked.connect(self.delete_profile)
        
        prof_layout.addWidget(self.profile_combo, 1)
        prof_layout.addWidget(btn_save)
        prof_layout.addWidget(btn_new)
        prof_layout.addWidget(btn_del)
        prof_group.setLayout(prof_layout)
        self.main_layout.addWidget(prof_group)

        # === 2. VIDEO CONFIG (Tarjeta Grid) ===
        vid_group = QGroupBox("Video y Captura")
        vid_layout = QGridLayout()
        vid_layout.setVerticalSpacing(20)
        vid_layout.setHorizontalSpacing(20)

        # Monitor Row (Full width)
        self.monitor_combo = QComboBox()
        btn_ref_mon = QPushButton("🔄")
        btn_ref_mon.setFixedWidth(40)
        btn_ref_mon.clicked.connect(self.detect_monitors)
        vid_layout.addWidget(QLabel("Pantalla Principal:"), 0, 0)
        vid_layout.addWidget(self.monitor_combo, 0, 1, 1, 2)
        vid_layout.addWidget(btn_ref_mon, 0, 3)

        # Parametros
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["ddagrab (GPU)", "gdigrab (CPU)"])
        vid_layout.addWidget(QLabel("Motor Captura:"), 1, 0); vid_layout.addWidget(self.mode_combo, 1, 1)

        self.fps_spin = QSpinBox(); self.fps_spin.setRange(30, 360); self.fps_spin.setValue(60); self.fps_spin.setSuffix(" FPS")
        vid_layout.addWidget(QLabel("Framerate:"), 1, 2); vid_layout.addWidget(self.fps_spin, 1, 3)

        self.bitrate_combo = QComboBox(); self.bitrate_combo.setEditable(True); self.bitrate_combo.addItems(["10000k", "25000k", "50000k", "80000k"])
        vid_layout.addWidget(QLabel("Bitrate (Calidad):"), 2, 0); vid_layout.addWidget(self.bitrate_combo, 2, 1)

        self.codec_combo = QComboBox(); self.codec_combo.addItems(["h264_nvenc (NVIDIA)", "hevc_nvenc (H.265)", "libx264 (CPU)"])
        vid_layout.addWidget(QLabel("Encoder:"), 2, 2); vid_layout.addWidget(self.codec_combo, 2, 3)
        
        # Buffer & Format
        self.replay_time_spin = QSpinBox(); self.replay_time_spin.setRange(5, 600); self.replay_time_spin.setSuffix(" s")
        vid_layout.addWidget(QLabel("Tiempo Buffer:"), 3, 0); vid_layout.addWidget(self.replay_time_spin, 3, 1)

        self.fmt_combo = QComboBox(); self.fmt_combo.addItems(["mkv", "mp4"])
        vid_layout.addWidget(QLabel("Contenedor:"), 3, 2); vid_layout.addWidget(self.fmt_combo, 3, 3)

        vid_group.setLayout(vid_layout)
        self.main_layout.addWidget(vid_group)

        # === 3. AUDIO MIXER (Tarjeta) ===
        audio_group = QGroupBox("Mezclador de Audio")
        audio_layout = QVBoxLayout()
        
        # Header audio
        audio_tools = QHBoxLayout()
        btn_refresh_audio = QPushButton("Recargar Disp.")
        btn_refresh_audio.clicked.connect(self.refresh_audio_ui)
        
        btn_add_track = QPushButton("Agregar Pista")
        btn_add_track.setStyleSheet("background-color: #2979FF; color: white; font-weight: bold; border: none;")
        btn_add_track.clicked.connect(lambda: self.add_audio_track())
        
        audio_tools.addWidget(btn_refresh_audio)
        audio_tools.addStretch()
        audio_tools.addWidget(btn_add_track)
        audio_layout.addLayout(audio_tools)

        # Area de pistas
        self.tracks_container = QWidget()
        self.tracks_layout = QVBoxLayout(self.tracks_container)
        self.tracks_layout.setContentsMargins(0,10,0,0)
        self.tracks_layout.setSpacing(10)
        audio_layout.addWidget(self.tracks_container)

        audio_group.setLayout(audio_layout)
        self.main_layout.addWidget(audio_group)

        # === 4. RUTA & ATAJOS (Dos columnas) ===
        row_settings = QHBoxLayout()
        
        # Ruta
        path_group = QGroupBox("Almacenamiento")
        path_layout = QVBoxLayout()
        path_row = QHBoxLayout()
        self.path_input = QLineEdit(self.recorder.settings["save_path"]); self.path_input.setReadOnly(True)
        btn_br = QPushButton("📂"); btn_br.setFixedWidth(40); btn_br.clicked.connect(self.browse_path)
        path_row.addWidget(self.path_input); path_row.addWidget(btn_br)
        path_layout.addLayout(path_row)
        path_group.setLayout(path_layout)
        
        # Hotkeys
        hk_group = QGroupBox("Atajos Globales")
        hk_layout = QGridLayout()
        self.rec_hk_disp = QLineEdit(); self.rec_hk_disp.setReadOnly(True); self.rec_hk_disp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rep_hk_disp = QLineEdit(); self.rep_hk_disp.setReadOnly(True); self.rep_hk_disp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_rec_hk = QPushButton("⚙️"); btn_rec_hk.setFixedWidth(40); btn_rec_hk.clicked.connect(lambda: self.start_hotkey_recording("rec"))
        btn_rep_hk = QPushButton("⚙️"); btn_rep_hk.setFixedWidth(40); btn_rep_hk.clicked.connect(lambda: self.start_hotkey_recording("replay"))
        
        hk_layout.addWidget(QLabel("Grabar / Stop:"), 0, 0); hk_layout.addWidget(self.rec_hk_disp, 0, 1); hk_layout.addWidget(btn_rec_hk, 0, 2)
        hk_layout.addWidget(QLabel("Guardar Replay:"), 1, 0); hk_layout.addWidget(self.rep_hk_disp, 1, 1); hk_layout.addWidget(btn_rep_hk, 1, 2)
        hk_group.setLayout(hk_layout)

        row_settings.addWidget(path_group, 1)
        row_settings.addWidget(hk_group, 1)
        self.main_layout.addLayout(row_settings)

        # === 5. BIG ACTION BUTTONS ===
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(20)
        ctrl_layout.setContentsMargins(0, 10, 0, 10)
        
        self.btn_rec = QPushButton("🔴 INICIAR GRABACIÓN")
        self.btn_rec.setObjectName("btn_rec_start")
        self.btn_rec.setMinimumHeight(60)
        self.btn_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rec.clicked.connect(self.toggle_recording)
        
        self.btn_buff = QPushButton("⚡ ACTIVAR BUFFER")
        self.btn_buff.setObjectName("btn_buff_start")
        self.btn_buff.setMinimumHeight(60)
        self.btn_buff.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buff.clicked.connect(self.toggle_buffer)
        
        self.btn_save = QPushButton("💾 GUARDAR CLIP")
        self.btn_save.setObjectName("btn_save_clip")
        self.btn_save.setMinimumHeight(60)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_replay)

        ctrl_layout.addWidget(self.btn_rec, 2)
        ctrl_layout.addWidget(self.btn_buff, 2)
        ctrl_layout.addWidget(self.btn_save, 1)
        self.main_layout.addLayout(ctrl_layout)

        # === 6. LOG CONSOLE ===
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(120)
        self.log_area.setPlaceholderText("Esperando acciones...")
        self.main_layout.addWidget(self.log_area)

        # Init Monitors
        self.detect_monitors()

    # ================= THEME LOGIC =================
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.btn_theme.setText("🌙")
        else:
            self.current_theme = "dark"
            self.btn_theme.setText("☀️")
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(get_stylesheet(self.current_theme))

    # ================= LOGICA AUDIO =================
    def detect_audio_devices_list(self):
        self.cached_audio_devices = audio_manager.get_audio_devices()
        self.log_message(f"Sistema de Audio: {len(self.cached_audio_devices)} dispositivos listos.")

    def refresh_audio_ui(self):
        self.detect_audio_devices_list()
        for combo, _ in self.audio_track_widgets:
            self._fill_audio_combo(combo)

    def _fill_audio_combo(self, combo, select_device_name=None):
        current_data = combo.currentData()
        combo.clear()
        
        for dev in self.cached_audio_devices:
            prefix = "🎤" if dev['type'] == 'input' else "🔊"
            display_text = f"{prefix} {dev['name']}"
            combo.addItem(display_text, userData=dev)
        
        target_name = select_device_name if select_device_name else (current_data['name'] if current_data else None)
        
        if target_name:
            found = False
            for i in range(combo.count()):
                data = combo.itemData(i)
                if data['name'] == target_name:
                    combo.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                combo.addItem(f"⚠️ [OFFLINE] {target_name}", userData={'name': target_name, 'index': -1})
                combo.setCurrentIndex(combo.count() - 1)

    def add_audio_track(self, preselect_name=None):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        combo = QComboBox()
        self._fill_audio_combo(combo, preselect_name)
        
        btn_del = QPushButton("✕")
        btn_del.setFixedWidth(35)
        btn_del.setObjectName("btn_delete") # Red style
        btn_del.clicked.connect(lambda: self.remove_audio_track(row_widget, combo))
        
        row_layout.addWidget(combo, 1)
        row_layout.addWidget(btn_del)
        
        self.tracks_layout.addWidget(row_widget)
        self.audio_track_widgets.append((combo, row_widget))

    def remove_audio_track(self, widget, combo):
        self.tracks_layout.removeWidget(widget)
        widget.deleteLater()
        self.audio_track_widgets = [t for t in self.audio_track_widgets if t[0] != combo]

    def get_configured_audio_tracks(self):
        tracks = []
        for combo, _ in self.audio_track_widgets:
            data = combo.currentData()
            if data and data.get('index') != -1:
                tracks.append(data)
        return tracks

    # ================= LOGICA PERFILES =================
    def load_startup_profile(self):
        names = self.profiles.get_profile_names()
        self.profile_combo.blockSignals(True)
        self.profile_combo.addItems(names)
        
        last = self.profiles.get_last_used_profile_name()
        if last and last in names:
            self.profile_combo.setCurrentText(last)
            self.load_profile_data(last)
        elif not names:
            self.create_default_profile()
        else:
            self.profile_combo.setCurrentIndex(0)
            self.load_profile_data(names[0])
        self.profile_combo.blockSignals(False)

    def create_default_profile(self):
        default = {
            "mode": "ddagrab (GPU)", "fps": 60, "bitrate": "10000k",
            "codec": "h264_nvenc (NVIDIA)", "time": 30, "fmt": "mkv",
            "hk_rec": "<f9>", "hk_rep": "<f10>", "monitor_idx": 0,
            "audio_tracks_names": []
        }
        self.profiles.save_profile("Default", default)
        self.profile_combo.addItem("Default")
        self.profile_combo.setCurrentText("Default")
        self.load_profile_data("Default")

    def on_profile_changed(self):
        name = self.profile_combo.currentText()
        if name:
            self.load_profile_data(name)
            self.profiles.set_last_used(name)

    def load_profile_data(self, name):
        data = self.profiles.get_profile_data(name)
        if not data: return
        
        self.mode_combo.setCurrentText(data.get("mode", "ddagrab"))
        self.fps_spin.setValue(data.get("fps", 60))
        self.bitrate_combo.setCurrentText(data.get("bitrate", "10000k"))
        self.codec_combo.setCurrentText(data.get("codec", "h264_nvenc"))
        self.replay_time_spin.setValue(data.get("time", 30))
        self.fmt_combo.setCurrentText(data.get("fmt", "mkv"))
        
        idx = self.monitor_combo.findData(data.get("monitor_idx", 0))
        if idx >= 0: self.monitor_combo.setCurrentIndex(idx)
        
        while self.audio_track_widgets:
            cb, w = self.audio_track_widgets[0]
            self.remove_audio_track(w, cb)
        
        saved_audios = data.get("audio_tracks_names", [])
        for dev_name in saved_audios:
            self.add_audio_track(preselect_name=dev_name)

        self.hotkey_rec_str = data.get("hk_rec", "<f9>")
        self.hotkey_replay_str = data.get("hk_rep", "<f10>")
        self.rec_hk_disp.setText(self.hotkey_rec_str)
        self.rep_hk_disp.setText(self.hotkey_replay_str)
        self.restart_hotkey_listener()
        
        self.log_message(f"Perfil '{name}' cargado.")

    def gather_ui_data(self):
        audio_names = []
        for combo, _ in self.audio_track_widgets:
            d = combo.currentData()
            if d: audio_names.append(d['name'])

        return {
            "mode": self.mode_combo.currentText(),
            "fps": self.fps_spin.value(),
            "bitrate": self.bitrate_combo.currentText(),
            "codec": self.codec_combo.currentText(),
            "time": self.replay_time_spin.value(),
            "fmt": self.fmt_combo.currentText(),
            "hk_rec": self.hotkey_rec_str,
            "hk_rep": self.hotkey_replay_str,
            "monitor_idx": self.monitor_combo.currentData(),
            "audio_tracks_names": audio_names
        }

    def save_current_profile(self):
        name = self.profile_combo.currentText()
        self.profiles.save_profile(name, self.gather_ui_data())
        self.log_message(f"Perfil '{name}' guardado.")

    def create_new_profile(self):
        name, ok = QInputDialog.getText(self, "Nuevo", "Nombre:")
        if ok and name:
            self.profiles.save_profile(name, self.gather_ui_data())
            self.profile_combo.addItem(name)
            self.profile_combo.setCurrentText(name)

    def delete_profile(self):
        name = self.profile_combo.currentText()
        if self.profile_combo.count() <= 1: return
        if QMessageBox.question(self, "Borrar", f"¿Eliminar '{name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.profiles.delete_profile(name)
            self.profile_combo.removeItem(self.profile_combo.currentIndex())
            self.on_profile_changed()

    # ================= CORE INTERACTION =================
    def apply_settings_to_core(self):
        br = self.bitrate_combo.currentText()
        if br.isdigit(): br += "k"
        
        mode_val = "ddagrab" if "ddagrab" in self.mode_combo.currentText() else "gdigrab"
        codec_val = "h264_nvenc" if "h264" in self.codec_combo.currentText() else "hevc_nvenc" if "hevc" in self.codec_combo.currentText() else "libx264"
        
        s = {
            "fps": self.fps_spin.value(),
            "bitrate": br,
            "codec": codec_val,
            "container": self.fmt_combo.currentText(),
            "save_path": self.path_input.text(),
            "replay_time": self.replay_time_spin.value(),
            "capture_mode": mode_val,
            "monitor_idx": self.monitor_combo.currentData(),
            "audio_tracks": self.get_configured_audio_tracks()
        }
        self.recorder.update_settings(s)

    def detect_monitors(self):
        current = self.monitor_combo.currentData()
        self.monitor_combo.clear()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            self.monitor_combo.addItem(f"Monitor {i} - {screen.name()}", userData=i)
        if current is not None:
            idx = self.monitor_combo.findData(current)
            if idx >= 0: self.monitor_combo.setCurrentIndex(idx)

    # ================= UTILS =================
    def log_message(self, msg):
        self.log_area.append(f"> {msg}")
        sb = self.log_area.verticalScrollBar(); sb.setValue(sb.maximum())
    
    def browse_path(self):
        d = QFileDialog.getExistingDirectory(self, "Carpeta"); 
        if d: self.path_input.setText(d)

    def update_rec_button_state(self): self.toggle_recording()
    def update_buffer_button_state(self): self.toggle_buffer()

    def toggle_recording(self):
        if not self.recorder.is_recording:
            self.apply_settings_to_core()
            tracks = self.get_configured_audio_tracks()
            if not tracks: self.log_message("⚠️ Grabando SIN AUDIO (No hay pistas).")
            
            try:
                self.recorder.start_recording()
                self.btn_rec.setText("⏹ DETENER GRABACIÓN")
                self.btn_rec.setObjectName("btn_rec_stop")
                self.apply_theme() # Refresh style for ID change
                self.log_message(f"🔴 Grabando...")
            except Exception as e: self.log_message(f"Error: {e}")
        else:
            self.recorder.stop_recording()
            self.btn_rec.setText("🔴 INICIAR GRABACIÓN")
            self.btn_rec.setObjectName("btn_rec_start")
            self.apply_theme()
            self.log_message("⬜ Grabación Guardada.")

    def toggle_buffer(self):
        if not self.recorder.is_replay_active:
            self.apply_settings_to_core()
            try:
                self.recorder.start_replay_buffer()
                self.btn_buff.setText("⏹ DETENER BUFFER")
                self.btn_buff.setObjectName("btn_buff_stop")
                self.apply_theme()
                self.btn_save.setEnabled(True)
                self.log_message(f"🟢 Buffer Activo (RAM).")
            except Exception as e: self.log_message(f"Error: {e}")
        else:
            self.recorder.stop_replay_buffer()
            self.btn_buff.setText("⚡ ACTIVAR BUFFER")
            self.btn_buff.setObjectName("btn_buff_start")
            self.apply_theme()
            self.btn_save.setEnabled(False)
            self.log_message("⚪ Buffer Cerrado.")

    def save_replay(self):
        if self.recorder.is_replay_active:
            self.signals.log.emit("💾 Guardando..."); threading.Thread(target=self._save_th).start()
    
    def _save_th(self):
        try: self.recorder.save_replay(); self.signals.log.emit("✅ Clip Guardado.")
        except Exception as e: self.signals.log.emit(f"❌ Error: {e}")

    # --- HOTKEYS ---
    def start_hotkey_recording(self, t):
        self.listening_for_new_hotkey = True; 
        if self.hotkey_listener: self.hotkey_listener.stop()
        threading.Thread(target=self._listen, args=(t,)).start()

    def _listen(self, t):
        cap = None; mods = set()
        def on_p(k):
            if k in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.shift_l, keyboard.Key.shift_r]: mods.add(k)
        def on_r(k):
            nonlocal cap
            if k in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.shift_l, keyboard.Key.shift_r]: 
                if k in mods: mods.remove(k)
                return
            p = []
            if any(m in mods for m in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]): p.append('<ctrl>')
            if any(m in mods for m in [keyboard.Key.alt_l, keyboard.Key.alt_r]): p.append('<alt>')
            if any(m in mods for m in [keyboard.Key.shift_l, keyboard.Key.shift_r]): p.append('<shift>')
            try: p.append(k.char.lower() if hasattr(k,'char') and k.char else f'<{k.name}>')
            except: p.append(str(k))
            cap = '+'.join(p); return False
        with keyboard.Listener(on_press=on_p, on_release=on_r) as l: l.join()
        self.signals.update_hotkey_ui.emit(t, cap)

    def update_hotkey_display(self, t, k):
        self.listening_for_new_hotkey = False
        if t == "rec": self.hotkey_rec_str = k; self.rec_hk_disp.setText(k)
        else: self.hotkey_replay_str = k; self.rep_hk_disp.setText(k)
        self.save_current_profile(); self.restart_hotkey_listener()

    def restart_hotkey_listener(self):
        if self.hotkey_listener: self.hotkey_listener.stop()
        try: self.hotkey_listener = keyboard.GlobalHotKeys({self.hotkey_rec_str: self.on_rec_hk, self.hotkey_replay_str: self.on_rep_hk}); self.hotkey_listener.start()
        except: pass

    def on_rec_hk(self): self.signals.update_rec_btn.emit()
    def on_rep_hk(self): self.save_replay()

    def closeEvent(self, e):
        if self.hotkey_listener: self.hotkey_listener.stop()
        self.recorder.stop_recording(); self.recorder.stop_replay_buffer(); e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())