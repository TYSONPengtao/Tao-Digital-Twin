@echo off
chcp 65001 >nul
setlocal
set "ROAM_BLENDER_EXE=D:\AJAVIS01\RHINO7.12\PLUGINS\BLENDER\RUNING\blender.exe"
if not exist "%ROAM_BLENDER_EXE%" set "ROAM_BLENDER_EXE="
if not defined ROAM_BLENDER_EXE for /f "delims=" %%B in ('where blender.exe 2^>nul') do if not defined ROAM_BLENDER_EXE set "ROAM_BLENDER_EXE=%%B"
if not defined ROAM_BLENDER_EXE (
  echo 找不到 Blender。请修改本启动文件中的 Blender 路径。
  pause
  exit /b 1
)
start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\Architecture_Complete_V24_23.blend"
