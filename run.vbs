Set WshShell = CreateObject("WScript.Shell")
' El "0" al final es el comando mágico para ocultar la ventana
WshShell.Run chr(34) & "run.bat" & chr(34), 0
Set WshShell = Nothing