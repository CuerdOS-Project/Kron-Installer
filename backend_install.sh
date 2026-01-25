#!/bin/bash
# backend_install.sh - Lógica de instalación extraída de void-installer
# Adaptado para ser controlado por una UI externa (Python/Qt)

# --- 1. CONFIGURACIÓN DEL ENTORNO ---

CONF_FILE="/tmp/.void-installer.conf"
TARGETDIR="/mnt/target"
LOG="/tmp/installation.log"
TARGET_FSTAB=$(mktemp -t vinstall-fstab-XXXXXXXX || exit 1)

# Preparar descriptores de archivo
# stdout (1) y stderr (2) van al LOG para depuración detallada
# fd3 va al stdout original para que Python lea los mensajes de estado ">>>"
exec 3>&1
exec >"$LOG" 2>&1

# Función para comunicar estado a la UI (Python)
log_ui() {
    echo ">>> $1" >&3
}

# Función para errores fatales
die() {
    log_ui "ERROR: $1"
    echo "ERROR FATAL: $1" >&2
    # Intentar desmontar por seguridad
    umount -R "$TARGETDIR" >/dev/null 2>&1
    exit 1
}

# Detectar EFI (Lógica original líneas 58-65)
if [ -e /sys/firmware/efi/systab ]; then
    EFI_SYSTEM=1
    EFI_FW_BITS=$(cat /sys/firmware/efi/fw_platform_size)
    if [ $EFI_FW_BITS -eq 32 ]; then
        EFI_TARGET=i386-efi
    else
        EFI_TARGET=x86_64-efi
    fi
fi

# --- 2. FUNCIONES DE UTILIDAD (Extraídas de installer.sh) ---

# Lee opciones del archivo generado por Python
get_option() {
    grep -E "^${1} .*" $CONF_FILE | sed -e "s|^${1} ||"
}

# Habilitar servicios (runit)
enable_service() {
    ln -sf "/etc/sv/$1" "$TARGETDIR/etc/runit/runsvdir/default/$1"
}

# --- 3. FUNCIONES CORE DE INSTALACIÓN ---

# Crea sistemas de archivos y monta particiones
create_filesystems() {
    local mnts dev mntpt fstype fspassno mkfs size rv uuid

    # Leer líneas MOUNTPOINT del config (ordenadas por punto de montaje)
    mnts=$(grep -E '^MOUNTPOINT .*' $CONF_FILE | sort -k 5)
    
    # Iterar sobre las particiones
    set -- ${mnts}
    while [ $# -ne 0 ]; do
        dev=$2; fstype=$3; mntpt="$5"; mkfs=$6
        shift 6

        echo "Procesando $dev ($fstype) para $mntpt..."

        # Configurar SWAP
        if [ "$fstype" = "swap" ]; then
            swapoff $dev >/dev/null 2>&1
            if [ "$mkfs" -eq 1 ]; then
                log_ui "Formateando Swap en $dev..."
                mkswap $dev || die "Fallo al crear swap en $dev"
            fi
            swapon $dev || die "Fallo al activar swap en $dev"
            uuid=$(blkid -o value -s UUID "$dev")
            echo "UUID=$uuid none swap defaults 0 0" >>$TARGET_FSTAB
            continue
        fi

        # Formatear particiones (Si mkfs=1)
        if [ "$mkfs" -eq 1 ]; then
            log_ui "Formateando $dev como $fstype..."
            case "$fstype" in
                btrfs) MKFS="mkfs.btrfs -f"; modprobe btrfs ;;
                ext2) MKFS="mke2fs -F"; modprobe ext2 ;;
                ext3) MKFS="mke2fs -F -j"; modprobe ext3 ;;
                ext4) MKFS="mke2fs -F -t ext4"; modprobe ext4 ;;
                f2fs) MKFS="mkfs.f2fs -f"; modprobe f2fs ;;
                vfat) MKFS="mkfs.vfat -F32"; modprobe vfat ;;
                xfs) MKFS="mkfs.xfs -f -i sparse=0"; modprobe xfs ;;
                *) die "Sistema de archivos $fstype no soportado" ;;
            esac
            
            $MKFS $dev || die "Fallo al formatear $dev ($fstype)"
        fi

        # Montar Root (/) primero
        if [ "$mntpt" = "/" ]; then
            mkdir -p $TARGETDIR
            mount -t $fstype $dev $TARGETDIR || die "Fallo al montar root en $dev"
            
            # Fstab para root
            uuid=$(blkid -o value -s UUID "$dev")
            if [ "$fstype" = "f2fs" -o "$fstype" = "btrfs" -o "$fstype" = "xfs" ]; then
                fspassno=0
            else
                fspassno=1
            fi
            echo "UUID=$uuid $mntpt $fstype defaults 0 $fspassno" >>$TARGET_FSTAB
        fi
    done

    # Montar el resto de particiones (que no son root ni swap)
    set -- ${mnts}
    while [ $# -ne 0 ]; do
        dev=$2; fstype=$3; mntpt="$5"
        shift 6
        [ "$mntpt" = "/" -o "$fstype" = "swap" ] && continue
        
        mkdir -p ${TARGETDIR}${mntpt}
        mount -t $fstype $dev ${TARGETDIR}${mntpt} || die "Fallo al montar $mntpt en $dev"
        
        uuid=$(blkid -o value -s UUID "$dev")
        if [ "$fstype" = "f2fs" -o "$fstype" = "btrfs" -o "$fstype" = "xfs" ]; then
            fspassno=0
        else
            fspassno=2
        fi
        echo "UUID=$uuid $mntpt $fstype defaults 0 $fspassno" >>$TARGET_FSTAB
    done
}

# Copiar sistema base desde el Live ISO (Local Source)
copy_rootfs() {
    log_ui "Copiando archivos del sistema..."
    # Usamos tar tal cual el original para preservar atributos extendidos
    tar --create --one-file-system --xattrs -f - / 2>/dev/null | \
        tar --extract --xattrs --xattrs-include='*' --preserve-permissions -f - -C $TARGETDIR
    
    if [ $? -ne 0 ]; then
        die "Error al copiar el sistema de archivos rootfs"
    fi
}

# Instalar paquetes desde red (Network Source)
install_packages() {
    log_ui "Descargando e instalando sistema base..."
    
    local _grub=""
    local _syspkg="base-system"

    # Determinar paquete GRUB necesario
    if [ "$(get_option BOOTLOADER)" != "none" ]; then
        if [ -n "$EFI_SYSTEM" ]; then
            if [ $EFI_FW_BITS -eq 32 ]; then
                _grub="grub-i386-efi"
            else
                _grub="grub-x86_64-efi"
            fi
        else
            _grub="grub"
        fi
    fi

    # Preparar claves XBPS
    mkdir -p $TARGETDIR/var/db/xbps/keys $TARGETDIR/usr/share
    cp -a /usr/share/xbps.d $TARGETDIR/usr/share/
    cp /var/db/xbps/keys/*.plist $TARGETDIR/var/db/xbps/keys
    mkdir -p $TARGETDIR/boot/grub

    # Instalar
    XBPS_ARCH=$(xbps-uhelper arch) xbps-install -r $TARGETDIR -SyU ${_syspkg} ${_grub} || die "Fallo xbps-install"
    
    # Reconfigurar
    xbps-reconfigure -r $TARGETDIR -f base-files
    chroot $TARGETDIR xbps-reconfigure -a || die "Fallo xbps-reconfigure"
}

# Montar sistemas virtuales para chroot
mount_filesystems() {
    for f in sys proc dev; do
        [ ! -d $TARGETDIR/$f ] && mkdir $TARGETDIR/$f
        mount --rbind /$f $TARGETDIR/$f
    done
}

# Desmontar todo al finalizar
umount_filesystems() {
    # Desactivar swap
    local mnts="$(grep -E '^MOUNTPOINT .* swap .*$' $CONF_FILE | sort -r -k 5)"
    set -- ${mnts}
    while [ $# -ne 0 ]; do
        local dev=$2; local fstype=$3
        shift 6
        if [ "$fstype" = "swap" ]; then
            swapoff $dev
        fi
    done
    # Desmontar recursivamente target
    umount -R $TARGETDIR
}

# --- 4. FUNCIONES DE CONFIGURACIÓN DEL SISTEMA ---

#
set_hostname() {
    local hostname="$(get_option HOSTNAME)"
    echo "${hostname:-void}" > $TARGETDIR/etc/hostname
}

#
set_timezone() {
    local TIMEZONE="$(get_option TIMEZONE)"
    ln -sf "/usr/share/zoneinfo/${TIMEZONE}" "${TARGETDIR}/etc/localtime"
}

#
set_locale() {
    local LOCALE="$(get_option LOCALE)"
    : "${LOCALE:=C.UTF-8}"
    sed -i -e "s|LANG=.*|LANG=$LOCALE|g" $TARGETDIR/etc/locale.conf
    sed -e "/${LOCALE}/s/^\#//" -i $TARGETDIR/etc/default/libc-locales
    chroot $TARGETDIR xbps-reconfigure -f glibc-locales
}

#
set_keymap() {
    local KEYMAP=$(get_option KEYMAP)
    # Console
    if [ -f /etc/vconsole.conf ]; then
        sed -i -e "s|KEYMAP=.*|KEYMAP=$KEYMAP|g" "$TARGETDIR/etc/vconsole.conf"
    else
        sed -i -e "s|#\?KEYMAP=.*|KEYMAP=$KEYMAP|g" "$TARGETDIR/etc/rc.conf"
    fi
    # Nota: Omito la configuración compleja de X11 por brevedad, 
    # pero puedes reactivarla copiando las líneas 291-308 del original si lo necesitas.
}

#
set_rootpassword() {
    echo "root:$(get_option ROOTPASSWORD)" | chroot $TARGETDIR chpasswd -c SHA512
}

#
set_useraccount() {
    local USERLOGIN="$(get_option USERLOGIN)"
    if [ -n "$USERLOGIN" ]; then
        chroot $TARGETDIR useradd -m -G "$(get_option USERGROUPS)" \
            -c "$(get_option USERNAME)" "$USERLOGIN"
        echo "$USERLOGIN:$(get_option USERPASSWORD)" | \
            chroot $TARGETDIR chpasswd -c SHA512
            
        # Sudoers
        if [ -d $TARGETDIR/etc/sudoers.d ]; then
            if [[ "$(get_option USERGROUPS)" != *"wheel"* ]]; then
                echo "$USERLOGIN ALL=(ALL:ALL) ALL" > "$TARGETDIR/etc/sudoers.d/$USERLOGIN"
            else
                echo "%wheel ALL=(ALL:ALL) ALL" > "$TARGETDIR/etc/sudoers.d/wheel"
            fi
        fi
    fi
}

declare -A MIRRORS

# Formato: ["nombre-logico"]="URL"
MIRRORS["Predeterminado"]="https://repo-default.voidlinux.org/"
MIRRORS["Europa, Finlandia"]="https://repo-fi.voidlinux.org/"
MIRRORS["Europa, Alemania"]="https://repo-de.voidlinux.org/"
MIRRORS["Global, CDN"]="https://repo-fastly.voidlinux.org/"
MIRRORS["Norte América, EEUU"]="https://mirrors.summithq.com/voidlinux/"

set_mirror() {
    local MIRROR_KEY=$(get_option MIRROR)
    local MIRROR_URL=${MIRRORS[$MIRROR_KEY]}

    if ! chroot $TARGETDIR xmirror -s $MIRROR_URL; then
        die "Fallo al configurar mirror $MIRROR_KEY ($MIRROR_URL)"
    fi
    log_ui "Mirror configurado: $MIRROR_KEY ($MIRROR_URL)"

    if ! chroot $TARGETDIR xbps-install -S; then
        die "Fallo al sincronizar repos"
    fi
    log_ui "Repos sincronizados"
}

enable_nonfree_repos() {
    log_ui "Activando repositorios no libres..."
    chroot $TARGETDIR xbps-install -Sy void-repo-nonfree || die "Fallo al instalar void-repo-nonfree"
    log_ui "Repositorios no libres activados."
}

get_nvidia_driver() {
    # Detectar tarjeta NVIDIA
    local info
    info=$(lspci | grep -i nvidia)

    # Extraer números de serie de la GPU (solo la primera coincidencia)
    local series
    series=$(echo "$info" | grep -oP '\b[0-9]{3,}\b' | head -n1)

    local driver=""

    if [ -n "$series" ]; then
        if [ "$series" -ge 800 ]; then
            driver="nvidia"
        elif [ "$series" -ge 600 ]; then
            driver="nvidia470"
        elif [ "$series" -ge 400 ]; then
            driver="nvidia390"
        fi
    fi
    # Si no se detecta serie o no entra en rangos soportados, driver=""
    echo "$driver"
}

install_nvidia_driver() {
    local driver
    driver=$(get_nvidia_driver)

    if [ -n "$driver" ]; then
        log_ui "Instalando driver NVIDIA: $driver..."
        chroot $TARGETDIR xbps-install -Sy "$driver" || die "Fallo al instalar driver $driver"
        log_ui "Driver NVIDIA instalado correctamente."
    else
        log_ui "No se detectó driver NVIDIA compatible, se usará nouveau/nvk."
    fi
}

install_intel_microcodes() {
    log_ui "Instalando microcódigos Intel..."
    chroot $TARGETDIR xbps-install -Sy intel-ucode || die "Fallo al instalar microcódigos Intel"
    log_ui "Microcódigos Intel instalados correctamente."
}

install_extra_software() {
    local nonfree=$(get_option NONFREE)   # checkbox de la GUI
    local nvidia=$(get_option NVIDIA)
    local intel=$(get_option INTEL)

    if [ "$nonfree" = "1" ]; then
        enable_nonfree_repos
        if [ "$nvidia" = "1" ]; then
            install_nvidia_driver
        fi

        if [ "$intel" = "1" ]; then
            install_intel_microcodes
        fi
    else
        log_ui "No se activaron repositorios no libres ni drivers NVIDIA."
    fi
}

# Instalar GRUB
set_bootloader() {
    local dev=$(get_option BOOTLOADER) grub_args=""
    
    if [ "$dev" = "none" ] || [ -z "$dev" ]; then return; fi
    
    if [ -n "$EFI_SYSTEM" ]; then
        grub_args="--target=$EFI_TARGET --efi-directory=/boot/efi --bootloader-id=void_grub --recheck"
    fi
    
    chroot $TARGETDIR grub-install $grub_args $dev || die "Error instalando GRUB en $dev"
    chroot $TARGETDIR grub-mkconfig -o /boot/grub/grub.cfg || die "Error generando grub.cfg"
}

# --- 5. ORQUESTACIÓN PRINCIPAL ---

# Validaciones previas
if [ "$(id -u)" != "0" ]; then
    echo "Este script debe ejecutarse como root" >&2
    exit 1
fi

if [ ! -f "$CONF_FILE" ]; then
    die "No se encontró $CONF_FILE. El frontend Python debe generarlo primero."
fi

log_ui "INICIANDO INSTALACIÓN..."
echo "Log iniciado en $LOG"

# Paso 1: Discos
log_ui "Preparando discos y particiones..."
create_filesystems

# Paso 2: Instalación Base
if [ "$(get_option SOURCE)" == "net" ]; then
    install_packages
else
    copy_rootfs
    
    # Limpieza post-copia live
    rm -f $TARGETDIR/etc/motd $TARGETDIR/etc/issue $TARGETDIR/usr/sbin/void-installer
    rm -f $TARGETDIR/etc/sddm.conf # Si existe
    # Eliminar usuario live del target
    chroot $TARGETDIR userdel -r anon >/dev/null 2>&1
    chroot $TARGETDIR userdel -r void >/dev/null 2>&1
fi

# Paso 3: Configuración
log_ui "Configurando sistema (Host, Hora, Idioma)..."
mount_filesystems
install -Dm644 $TARGET_FSTAB $TARGETDIR/etc/fstab
echo "tmpfs /tmp tmpfs defaults,nosuid,nodev 0 0" >> $TARGETDIR/etc/fstab

set_keymap
set_locale
set_timezone
set_hostname

log_ui "Configurando mirror..."
set_mirror
install_extra_software

log_ui "Configurando usuarios..."
set_rootpassword
set_useraccount

# Paso 4: Bootloader
log_ui "Instalando Bootloader (GRUB)..."
set_bootloader

# Paso 5: Finalizar
log_ui "Finalizando y desmontando..."
sync
umount_filesystems
rm -f $TARGET_FSTAB

log_ui "INSTALACIÓN COMPLETADA"
exit 0