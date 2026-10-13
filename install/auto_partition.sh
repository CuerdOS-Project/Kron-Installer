#!/bin/bash
# auto_partition.sh

# Cualquier comando que falle detiene el script con código distinto de 0,
# para que la interfaz no diga "particionado correcto" si algo salió mal.
set -e

DISK="$1"
TARGET="/mnt/target"

if [ -z "$DISK" ]; then
    echo "Uso: $0 /dev/sdX"
    exit 1
fi

if [ ! -b "$DISK" ]; then
    echo "Error: $DISK no es un dispositivo de bloques." >&2
    exit 1
fi

# Seguridad: no tocar un disco con particiones montadas (p.ej. el USB live
# desde el que se arrancó). Hay que desmontarlas antes.
MONTADAS="$(lsblk -nro MOUNTPOINT "$DISK" | grep -v '^$' | grep -vx '\[SWAP\]' || true)"
if [ -n "$MONTADAS" ]; then
    echo "Error: $DISK tiene particiones montadas ($(echo $MONTADAS)). Desmóntalas antes de continuar." >&2
    exit 1
fi

# Confirmar EFI
EFI=0
if [ -e /sys/firmware/efi ]; then
    EFI=1
fi

# Advertencia: borra TODO en el disco
sgdisk --zap-all "$DISK"

if [ $EFI -eq 1 ]; then
    # Crear GPT
    sgdisk -o "$DISK"
    # Partición EFI: 512 MiB
    sgdisk -n 1:2048:+512M -t 1:ef00 "$DISK"
    # Partición root: resto del disco
    sgdisk -n 2:0:0 -t 2:8300 "$DISK"
else
    # Crear MBR
    parted -s "$DISK" mklabel msdos
    # Partición ESP: 512 MiB (Limine solo lee FAT32, incluso en BIOS)
    parted -s "$DISK" mkpart primary fat32 1MiB 513MiB
    parted -s "$DISK" set 1 esp on
    # Partición root: resto del disco
    parted -s "$DISK" mkpart primary 513MiB 100%
fi

# Avisar al kernel de la nueva tabla y esperar a que udev cree los nodos,
# para que la recarga de particiones de la interfaz vea el estado final.
partprobe "$DISK" || true
udevadm settle || true

echo "Particionado automático completado en $DISK"

