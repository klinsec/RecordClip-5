@echo off
title Instalador de Dependencias - RecordClip Studio
color 0B

echo ==================================================
echo   INSTALANDO DEPENDENCIAS DE VIDEO (PyQt6...)
echo ==================================================
pip install PyQt6 pynput

echo.
echo ==================================================
echo   INSTALANDO DEPENDENCIAS DE AUDIO (FIX NUMPY)
echo   * Se forzara una version compatible de NumPy
echo ==================================================
:: Este comando es vital para que soundcard no falle
pip install "numpy<2.0" soundcard soundfile --force-reinstall

echo.
echo ==================================================
echo   INSTALACION COMPLETADA
echo ==================================================
pause