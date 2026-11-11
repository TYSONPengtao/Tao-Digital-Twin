@echo off
chcp 65001 >nul
setlocal
set "V25_RHINO_EXE=D:\AJAVIS01\RHINO8\RUNING\System\Rhino.exe"
if not exist "%V25_RHINO_EXE%" (
  echo 请使用 Rhino 8 打开 Rhino 文件夹中的 3dm 文件。
  pause
  exit /b 1
)
start "" "%V25_RHINO_EXE%" "%~dp0Rhino\Architecture_Complete_V25_ALIGNED_ENU.3dm"
