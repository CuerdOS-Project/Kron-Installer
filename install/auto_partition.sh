#!/bin/bash
# auto_partition.sh
# Uso: pkexec bash auto_partition.sh /dev/sdX

DISK="$1"
TARGET="/mnt/target"

if [ -z "$DISK" ]; then
    echo "Uso: $0 /dev/sdX"
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
    # Partición root: todo el disco
    parted -s "$DISK" mkpart primary 1MiB 100%
fi

echo "Particionado automático completado en $DISK"

