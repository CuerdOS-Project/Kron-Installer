#!/bin/bash
#
# Script para actualizar y compilar traducciones Qt del Instalador Almazara
# Uso: ./update_translations.sh [comando]
#
# Requisitos: pyside6-lupdate, pyside6-lrelease (parte de PySide6)
#
# Comandos:
#   update   - Actualiza los archivos .ts con las nuevas cadenas del código
#   compile  - Compila los archivos .ts a .qm
#   all      - Actualiza y compila (por defecto)
#   status   - Muestra el estado de las traducciones
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Directorio de traducciones
I18N_DIR="i18n"

# Lista de idiomas disponibles
LANGUAGES="es en de eu gl fr ca pt_BR it"

# Archivos a escanear
SCAN_FILES="main.py ui/*.py install/*.py"

# Verificar que las herramientas existen
check_tools() {
    if ! command -v pyside6-lupdate &> /dev/null; then
        echo -e "${RED}✗ Error: pyside6-lupdate no encontrado${NC}"
        echo -e "${YELLOW}  Instala PySide6: pip install PySide6${NC}"
        exit 1
    fi
    if ! command -v pyside6-lrelease &> /dev/null; then
        echo -e "${RED}✗ Error: pyside6-lrelease no encontrado${NC}"
        echo -e "${YELLOW}  Instala PySide6: pip install PySide6${NC}"
        exit 1
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Almazara Installer - Traducciones Qt     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Función para actualizar archivos .ts
update_translations() {
    check_tools
    echo -e "${YELLOW}📡 Actualizando archivos de traducción (.ts)...${NC}"
    echo ""
    
    for lang in $LANGUAGES; do
        ts_file="$I18N_DIR/$lang.ts"
        echo -e "  ${GREEN}→${NC} Procesando: ${BLUE}$lang${NC}"
        
        if [ -f "$ts_file" ]; then
            pyside6-lupdate $SCAN_FILES -ts "$ts_file" -locations relative 2>/dev/null || true
        else
            echo -e "    ${YELLOW}Creando nuevo archivo: $ts_file${NC}"
            pyside6-lupdate $SCAN_FILES -ts "$ts_file" -locations relative 2>/dev/null || true
        fi
    done
    
    echo ""
    echo -e "${GREEN}✓ Archivos .ts actualizados${NC}"
}

# Función para compilar archivos .qm
compile_translations() {
    check_tools
    echo -e "${YELLOW}🔨 Compilando archivos de traducción (.qm)...${NC}"
    echo ""
    
    for lang in $LANGUAGES; do
        ts_file="$I18N_DIR/$lang.ts"
        qm_file="$I18N_DIR/$lang.qm"
        
        if [ -f "$ts_file" ]; then
            echo -e "  ${GREEN}→${NC} Compilando: ${BLUE}$lang${NC}"
            pyside6-lrelease "$ts_file" -qm "$qm_file" 2>/dev/null || true
        else
            echo -e "  ${RED}✗${NC} No existe: $ts_file"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✓ Archivos .qm compilados${NC}"
}

# Función para mostrar estado
show_status() {
    echo -e "${YELLOW}📊 Estado de las traducciones:${NC}"
    echo ""
    echo -e "  ${BLUE}Idioma${NC}      ${BLUE}Archivo .ts${NC}          ${BLUE}Archivo .qm${NC}"
    echo -e "  ─────────────────────────────────────────────────"
    
    for lang in $LANGUAGES; do
        ts_file="$I18N_DIR/$lang.ts"
        qm_file="$I18N_DIR/$lang.qm"
        
        ts_status="❌ No existe"
        qm_status="❌ No existe"
        
        if [ -f "$ts_file" ]; then
            size=$(stat -c%s "$ts_file" 2>/dev/null || stat -f%z "$ts_file" 2>/dev/null || echo "0")
            ts_status="✅ ${size} bytes"
        fi
        
        if [ -f "$qm_file" ]; then
            size=$(stat -c%s "$qm_file" 2>/dev/null || stat -f%z "$qm_file" 2>/dev/null || echo "0")
            qm_status="✅ ${size} bytes"
        fi
        
        printf "  %-12s %-20s %s\n" "$lang" "$ts_status" "$qm_status"
    done
    
    echo ""
    
    # Contar mensajes pendientes de traducir
    echo -e "${YELLOW}📝 Mensajes sin traducir por idioma:${NC}"
    echo ""
    
    for lang in $LANGUAGES; do
        ts_file="$I18N_DIR/$lang.ts"
        if [ -f "$ts_file" ]; then
            # Contar traducciones vacías
            empty=$(grep -c '<translation></translation>' "$ts_file" 2>/dev/null || true)
            total=$(grep -c '<source>' "$ts_file" 2>/dev/null || true)
            
            # Convertir a número, default 0 si está vacío
            empty=${empty:-0}
            total=${total:-0}
            
            if [ "$empty" -gt 0 ]; then
                echo -e "  ${YELLOW}$lang${NC}: $empty de $total mensajes sin traducir"
            else
                echo -e "  ${GREEN}$lang${NC}: ✓ Completo ($total mensajes)"
            fi
        fi
    done
}

# Función de ayuda
show_help() {
    echo -e "${YELLOW}Uso:${NC} $0 [comando]"
    echo ""
    echo -e "${YELLOW}Comandos disponibles:${NC}"
    echo -e "  ${GREEN}update${NC}   - Actualiza los archivos .ts con las nuevas cadenas"
    echo -e "  ${GREEN}compile${NC}  - Compila los archivos .ts a .qm"
    echo -e "  ${GREEN}all${NC}      - Actualiza y compila (por defecto)"
    echo -e "  ${GREEN}status${NC}   - Muestra el estado de las traducciones"
    echo -e "  ${GREEN}apply${NC}    - Aplica las traducciones automáticas (script Python)"
    echo -e "  ${GREEN}help${NC}     - Muestra esta ayuda"
    echo ""
    echo -e "${YELLOW}Idiomas soportados:${NC} $LANGUAGES"
    echo ""
    echo -e "${YELLOW}Flujo de trabajo recomendado:${NC}"
    echo -e "  1. ${BLUE}./update_translations.sh update${NC}   - Actualizar .ts con nuevas cadenas"
    echo -e "  2. ${BLUE}./apply_translations.py${NC}           - Aplicar traducciones automáticas"
    echo -e "  3. ${BLUE}./update_translations.sh compile${NC}  - Compilar a .qm"
}

# Procesar comando
COMMAND="${1:-all}"

case "$COMMAND" in
    update)
        update_translations
        ;;
    compile)
        compile_translations
        ;;
    all)
        update_translations
        echo ""
        compile_translations
        ;;
    status)
        show_status
        ;;
    apply)
        python3 apply_translations.py
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Comando desconocido: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"

