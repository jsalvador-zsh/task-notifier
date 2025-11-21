@echo off
REM ###########################################################################
REM Script de Compilación para Windows - Task Notifier
REM
REM Este script genera automáticamente un ejecutable .exe
REM para Windows que NO requiere Python instalado.
REM
REM Uso: Doble clic en build_windows.bat o ejecutar desde CMD
REM ###########################################################################

setlocal EnableDelayedExpansion

REM Variables
set "APP_NAME=TaskNotifier"
set "SCRIPT_DIR=%~dp0"
set "BUILD_DIR=%SCRIPT_DIR%build"
set "DIST_DIR=%SCRIPT_DIR%dist"
set "VENV_DIR=%SCRIPT_DIR%venv_build"

cls
echo ================================================================
echo    Task Notifier - Constructor de Aplicacion para Windows
echo ================================================================
echo.

REM Verificar que estamos en Windows
if not "%OS%"=="Windows_NT" (
    echo [ERROR] Este script solo funciona en Windows
    echo         Para macOS, usa: ./build_macos.sh
    pause
    exit /b 1
)

REM Paso 1: Verificar Python
echo [Paso 1/7] Verificando Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado
    echo         Descarga Python desde: https://www.python.org/downloads/
    echo         Asegurate de marcar "Add Python to PATH" durante instalacion
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% encontrado
echo.

REM Paso 2: Crear entorno virtual limpio
echo [Paso 2/7] Preparando entorno de compilacion...
if exist "%VENV_DIR%" (
    echo          Limpiando entorno anterior...
    rmdir /s /q "%VENV_DIR%" 2>nul
)

python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
echo [OK] Entorno virtual creado
echo.

REM Paso 3: Instalar dependencias
echo [Paso 3/7] Instalando dependencias...
echo          Actualizando pip...
python -m pip install --upgrade pip wheel setuptools >nul 2>&1
echo          Instalando requirements...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias
    echo         Verifica que requirements.txt existe
    pause
    exit /b 1
)

echo          Instalando PyInstaller...
pip install pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Paso 4: Limpiar builds anteriores
echo [Paso 4/7] Limpiando builds anteriores...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%" 2>nul
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%" 2>nul
del /q "%SCRIPT_DIR%*.spec" 2>nul
echo [OK] Directorios limpiados
echo.

REM Paso 5: Verificar archivos necesarios
echo [Paso 5/7] Verificando archivos necesarios...
set "MISSING_FILES="

if not exist "%SCRIPT_DIR%main.py" set "MISSING_FILES=!MISSING_FILES! main.py"
if not exist "%SCRIPT_DIR%gui_flet.py" set "MISSING_FILES=!MISSING_FILES! gui_flet.py"
if not exist "%SCRIPT_DIR%config.py" set "MISSING_FILES=!MISSING_FILES! config.py"

if not "!MISSING_FILES!"=="" (
    echo [ERROR] Archivos faltantes:!MISSING_FILES!
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%image.png" (
    echo [WARN] image.png no encontrado ^(avatar^)
)

if not exist "%SCRIPT_DIR%.env" (
    echo [WARN] .env no encontrado
)

echo [OK] Archivos verificados
echo.

REM Paso 6: Generar ejecutable
echo [Paso 6/7] Generando ejecutable .exe ^(esto puede tardar varios minutos^)...
echo          Por favor espera...

REM Construir comando PyInstaller
set "CMD=pyinstaller"
set "CMD=!CMD! --name=%APP_NAME%"
set "CMD=!CMD! --onedir"
set "CMD=!CMD! --windowed"
set "CMD=!CMD! --noconfirm"
set "CMD=!CMD! --clean"
set "CMD=!CMD! --add-data=config.py;."
set "CMD=!CMD! --add-data=gui_flet.py;."
set "CMD=!CMD! --hidden-import=tkinter"
set "CMD=!CMD! --hidden-import=PIL"
set "CMD=!CMD! --hidden-import=psycopg2"
set "CMD=!CMD! --hidden-import=pygame"

REM Agregar archivos opcionales
if exist "%SCRIPT_DIR%image.png" (
    set "CMD=!CMD! --add-data=image.png;."
)

if exist "%SCRIPT_DIR%.env" (
    set "CMD=!CMD! --add-data=.env;."
)

set "CMD=!CMD! main.py"

REM Ejecutar PyInstaller
!CMD! >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller fallo
    echo         Ejecuta el script de nuevo para ver errores detallados
    pause
    exit /b 1
)

echo [OK] Ejecutable generado
echo.

REM Paso 7: Verificar resultado
echo [Paso 7/7] Verificando resultado...
set "EXE_PATH=%DIST_DIR%\%APP_NAME%\%APP_NAME%.exe"

if exist "%EXE_PATH%" (
    echo [OK] Ejecutable creado exitosamente
    echo.
    echo ================================================================
    echo                   COMPILACION EXITOSA
    echo ================================================================
    echo.
    echo Ejecutable listo:
    echo    Ubicacion: %DIST_DIR%\%APP_NAME%\
    echo    Archivo: %APP_NAME%.exe
    echo.
    echo Como usar:
    echo    1. Abre el Explorador de Windows
    echo    2. Navega a: %DIST_DIR%\%APP_NAME%\
    echo    3. Haz doble clic en: %APP_NAME%.exe
    echo.
    echo Notas importantes:
    echo    - Windows Defender puede mostrar una advertencia
    echo    - Haz clic en "Mas informacion" ^> "Ejecutar de todas formas"
    echo    - El ejecutable incluye TODOS los archivos necesarios
    echo.
    echo Configuracion de base de datos:
    echo    - Edita config.py antes de distribuir
    echo    - O coloca un archivo .env junto al .exe
    echo.
    echo Para distribuir:
    echo    1. Comprime toda la carpeta "%APP_NAME%" en un ZIP
    echo    2. Comparte el ZIP con otros usuarios de Windows
    echo    3. Los usuarios pueden extraer y ejecutar sin instalar Python
    echo.
    echo ================================================================
    echo.

    REM Preguntar si quiere abrir la carpeta
    set /p OPEN_FOLDER="Abrir carpeta de distribucion? [S/N]: "
    if /i "!OPEN_FOLDER!"=="S" (
        explorer "%DIST_DIR%"
    )

) else (
    echo [ERROR] No se pudo crear el ejecutable
    echo         Revisa los errores anteriores
    pause
    exit /b 1
)

REM Limpiar archivos temporales
echo.
echo Limpiando archivos temporales...
call "%VENV_DIR%\Scripts\deactivate.bat" 2>nul
rmdir /s /q "%VENV_DIR%" 2>nul
rmdir /s /q "%BUILD_DIR%" 2>nul
del /q "%SCRIPT_DIR%\%APP_NAME%.spec" 2>nul
echo [OK] Limpieza completada
echo.

echo Todo listo!
echo.
pause
