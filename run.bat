@echo off
title RecordClip Studio Pro
color 0A

echo Iniciando RecordClip Studio...
echo No cierres esta ventana (aqui veras los logs de errores).
echo.

python main_ui.py

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo [ERROR] El programa se cerro inesperadamente.
    pause
)