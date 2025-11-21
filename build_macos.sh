#!/bin/bash
###############################################################################
# Script de Compilación para macOS - Task Notifier
#
# Este script genera automáticamente una aplicación .app ejecutable
# para macOS que NO requiere Python instalado ni abrir terminal.
#
# Uso: ./build_macos.sh
###############################################################################

set -e  # Detener en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Task Notifier"
BUILD_DIR="$SCRIPT_DIR/build"
DIST_DIR="$SCRIPT_DIR/dist"
VENV_DIR="$SCRIPT_DIR/venv_build"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Task Notifier - Constructor de Aplicación para macOS    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Error: Este script solo funciona en macOS${NC}"
    echo -e "${YELLOW}   Para Windows, usa: build_windows.bat${NC}"
    exit 1
fi

# Paso 1: Verificar Python
echo -e "${YELLOW}📋 Paso 1: Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo -e "${YELLOW}   Instala Python desde: https://www.python.org/downloads/${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION encontrado${NC}"
echo ""

# Paso 2: Crear entorno virtual limpio para build
echo -e "${YELLOW}📋 Paso 2: Preparando entorno de compilación...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo "   Limpiando entorno anterior..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✅ Entorno virtual creado${NC}"
echo ""

# Paso 3: Instalar dependencias
echo -e "${YELLOW}📋 Paso 3: Instalando dependencias...${NC}"
pip install --upgrade pip wheel setuptools > /dev/null 2>&1
echo "   Instalando requirements..."
pip install -r requirements.txt > /dev/null 2>&1
echo "   Instalando PyInstaller..."
pip install pyinstaller > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo ""

# Paso 4: Limpiar builds anteriores
echo -e "${YELLOW}📋 Paso 4: Limpiando builds anteriores...${NC}"
rm -rf "$BUILD_DIR"
rm -rf "$DIST_DIR"
rm -rf "$SCRIPT_DIR/*.spec"
echo -e "${GREEN}✅ Directorios limpiados${NC}"
echo ""

# Paso 5: Verificar archivos necesarios
echo -e "${YELLOW}📋 Paso 5: Verificando archivos necesarios...${NC}"
REQUIRED_FILES=("main.py" "gui_flet.py" "config.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${RED}❌ Archivos faltantes:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Verificar imagen (opcional)
if [ ! -f "$SCRIPT_DIR/image.png" ]; then
    echo -e "${YELLOW}⚠️  Advertencia: image.png no encontrado (avatar)${NC}"
fi

# Verificar .env (opcional)
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Advertencia: .env no encontrado${NC}"
fi

echo -e "${GREEN}✅ Archivos verificados${NC}"
echo ""

# Paso 6: Crear el ejecutable con PyInstaller
echo -e "${YELLOW}📋 Paso 6: Generando aplicación .app (esto puede tardar)...${NC}"

# Opciones de PyInstaller:
# --name: Nombre de la aplicación
# --onedir: Crear un directorio con todos los archivos
# --windowed: Sin ventana de consola
# --icon: Icono de la aplicación (si existe)
# --add-data: Agregar archivos adicionales
# --hidden-import: Importar módulos ocultos
# --noconfirm: No pedir confirmación

PYINSTALLER_OPTS=(
    --name="$APP_NAME"
    --onedir
    --windowed
    --noconfirm
    --clean
    --add-data="config.py:."
    --add-data="gui_flet.py:."
    --hidden-import="tkinter"
    --hidden-import="PIL"
    --hidden-import="psycopg2"
    --hidden-import="pygame"
)

# Agregar image.png si existe
if [ -f "$SCRIPT_DIR/image.png" ]; then
    PYINSTALLER_OPTS+=(--add-data="image.png:.")
fi

# Agregar .env si existe
if [ -f "$SCRIPT_DIR/.env" ]; then
    PYINSTALLER_OPTS+=(--add-data=".env:.")
fi

# Ejecutar PyInstaller
pyinstaller "${PYINSTALLER_OPTS[@]}" main.py

echo -e "${GREEN}✅ Aplicación generada${NC}"
echo ""

# Paso 7: Verificar resultado
echo -e "${YELLOW}📋 Paso 7: Verificando resultado...${NC}"
APP_PATH="$DIST_DIR/$APP_NAME.app"

if [ -d "$APP_PATH" ]; then
    echo -e "${GREEN}✅ Aplicación creada exitosamente${NC}"

    # Obtener tamaño
    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)

    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    ¡COMPILACIÓN EXITOSA!                   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}📦 Aplicación lista:${NC}"
    echo -e "   Ubicación: $APP_PATH"
    echo -e "   Tamaño: $APP_SIZE"
    echo ""
    echo -e "${GREEN}🚀 Cómo usar:${NC}"
    echo -e "   1. Abre Finder"
    echo -e "   2. Navega a: $DIST_DIR"
    echo -e "   3. Haz doble clic en: $APP_NAME.app"
    echo ""
    echo -e "${YELLOW}📝 Nota importante:${NC}"
    echo -e "   - La primera vez macOS puede mostrar advertencia de seguridad"
    echo -e "   - Clic derecho > Abrir para permitir la ejecución"
    echo -e "   - O ve a: Preferencias del Sistema > Seguridad y Privacidad"
    echo ""
    echo -e "${GREEN}📋 Configuración de la base de datos:${NC}"
    echo -e "   - Edita las credenciales en config.py antes de distribuir"
    echo -e "   - O crea un archivo .env junto a la aplicación"
    echo ""
    echo -e "${BLUE}✨ Para distribuir:${NC}"
    echo -e "   1. Comprime el archivo .app en un ZIP"
    echo -e "   2. Comparte el ZIP con otros usuarios de macOS"
    echo -e "   3. Los usuarios pueden extraer y ejecutar sin instalar nada"
    echo ""

    # Preguntar si quiere abrir la carpeta
    read -p "$(echo -e ${GREEN}¿Abrir carpeta de distribución? [s/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        open "$DIST_DIR"
    fi

else
    echo -e "${RED}❌ Error: No se pudo crear la aplicación${NC}"
    echo -e "${YELLOW}   Revisa los errores anteriores${NC}"
    exit 1
fi

# Limpiar entorno de build
echo ""
echo -e "${YELLOW}🧹 Limpiando archivos temporales...${NC}"
deactivate 2>/dev/null || true
rm -rf "$VENV_DIR"
rm -rf "$BUILD_DIR"
rm -f "$SCRIPT_DIR/$APP_NAME.spec"
echo -e "${GREEN}✅ Limpieza completada${NC}"

echo ""
echo -e "${GREEN}🎉 ¡Todo listo!${NC}"
