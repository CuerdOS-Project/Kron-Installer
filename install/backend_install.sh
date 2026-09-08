#!/bin/bash
# Lógica de instalación extraída de void-installer

# --- 1. CONFIGURACIÓN DEL ENTORNO ---

CONF_FILE="/tmp/.void-installer.conf"
TARGETDIR="/mnt/target"
LOG="/tmp/installation.log"
TARGET_FSTAB=$(mktemp -t vinstall-fstab-XXXXXXXX || exit 1)

# Preparar descriptores de archivo
# stdout (1) y stderr (2) van al LOG para depuración detallada
# fd3 va al stdout original para que Python lea los mensajes de estado ">>>"
exec 3>&1
exec > >(tee -a "$LOG") 2>&1

# Función para comunicar estado a la UI (Python)
log_ui() {
    echo ">>> $1" >&3
}

# Función para errores fatales
die() {
    log_ui "ERROR: $1"
    echo "FATAL ERROR: $1" >&2
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
    grep -E "^${1} .*" "$CONF_FILE" | sed -e "s|^${1} ||"
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
    mnts=$(grep -E '^MOUNTPOINT .*' "$CONF_FILE" | sort -k 5)
    
    # Iterar sobre las particiones
    set -- ${mnts}
    while [ $# -ne 0 ]; do
        dev=$2; fstype=$3; mntpt="$5"; mkfs=$6
        shift 6

        echo "Procesando $dev ($fstype) para $mntpt..."

        # Configurar SWAP
        if [ "$fstype" = "swap" ]; then
            swapoff "$dev" >/dev/null 2>&1
            if [ "$mkfs" -eq 1 ]; then
                echo "Formatting Swap on $dev..."
                mkswap "$dev" || die "Error creating swap on $dev"
            fi
            swapon "$dev" || die "Error activating swap on $dev"
            uuid=$(blkid -o value -s UUID "$dev")
            echo "UUID=$uuid none swap defaults 0 0" >>"$TARGET_FSTAB"
            continue
        fi

        # Formatear particiones (Si mkfs=1)
        if [ "$mkfs" -eq 1 ]; then
            echo "Formatting $dev as $fstype..."
            case "$fstype" in
                btrfs) MKFS="mkfs.btrfs"; MKFS_FLAGS="-f"; modprobe btrfs ;;
                ext2) MKFS="mke2fs"; MKFS_FLAGS="-F"; modprobe ext2 ;;
                ext3) MKFS="mke2fs"; MKFS_FLAGS="-F -j"; modprobe ext3 ;;
                ext4) MKFS="mke2fs"; MKFS_FLAGS="-F -t ext4"; modprobe ext4 ;;
                f2fs) MKFS="mkfs.f2fs"; MKFS_FLAGS="-f"; modprobe f2fs ;;
                vfat) MKFS="mkfs.vfat"; MKFS_FLAGS="-F32"; modprobe vfat ;;
                xfs) MKFS="mkfs.xfs"; MKFS_FLAGS="-f -i sparse=0"; modprobe xfs ;;
                *) die "File system $fstype not supported" ;;
            esac
            
            $MKFS $MKFS_FLAGS "$dev" || die "Error formatting $dev ($fstype)"
        fi

        # Montar Root (/) primero
        if [ "$mntpt" = "/" ]; then
            mkdir -p "$TARGETDIR"

            if [ "$fstype" = "btrfs" ]; then
                echo "Creating BTRFS subvolumes..."

                # Montaje temporal sin subvol
                mount "$dev" "$TARGETDIR" || die "Error when mounting temporary BTRFS"

                # Subvolúmenes estándar
                btrfs subvolume create "$TARGETDIR/@" || die "Error creating @"
                btrfs subvolume create "$TARGETDIR/@home" || die "Error creating @home"
                btrfs subvolume create "$TARGETDIR/@log" || die "Error creating @log"
                btrfs subvolume create "$TARGETDIR/@pkg" || die "Error creating @pkg"

                umount "$TARGETDIR"

                # Montaje definitivo del root
                mount -o subvol=@ "$dev" "$TARGETDIR" || die "Error mounting subvol @"

                mkdir -p "$TARGETDIR/home"
                mkdir -p "$TARGETDIR/var/log"
                mkdir -p "$TARGETDIR/var/cache/xbps"

                mount -o subvol=@home "$dev" "$TARGETDIR/home"
                mount -o subvol=@log  "$dev" "$TARGETDIR/var/log"
                mount -o subvol=@pkg  "$dev" "$TARGETDIR/var/cache/xbps"

                uuid=$(blkid -o value -s UUID "$dev")
                echo "UUID=$uuid / btrfs defaults,subvol=@ 0 0" >>"$TARGET_FSTAB"
                echo "UUID=$uuid /home btrfs defaults,subvol=@home 0 0" >>"$TARGET_FSTAB"
                echo "UUID=$uuid /var/log btrfs defaults,subvol=@log 0 0" >>"$TARGET_FSTAB"
                echo "UUID=$uuid /var/cache/xbps btrfs defaults,subvol=@pkg 0 0" >>"$TARGET_FSTAB"

                continue
            fi

            mount -t "$fstype" "$dev" "$TARGETDIR" || die "Error mounting root on $dev"
            
            # Fstab para root
            uuid=$(blkid -o value -s UUID "$dev")
            if [ "$fstype" = "f2fs" ] || [ "$fstype" = "btrfs" ] || [ "$fstype" = "xfs" ]; then
                fspassno=0
            else
                fspassno=1
            fi
            echo "UUID=$uuid $mntpt $fstype defaults 0 $fspassno" >>"$TARGET_FSTAB"
        fi
    done

    # Montar el resto de particiones (que no son root ni swap)
    set -- ${mnts}
    while [ $# -ne 0 ]; do
        dev=$2; fstype=$3; mntpt="$5"
        shift 6
        [ "$mntpt" = "/" ] || [ "$fstype" = "swap" ] && continue
        
        mkdir -p "${TARGETDIR}${mntpt}"
        mount -t "$fstype" "$dev" "${TARGETDIR}${mntpt}" || die "Error mounting $mntpt on $dev"
        
        uuid=$(blkid -o value -s UUID "$dev")
        if [ "$fstype" = "f2fs" ] || [ "$fstype" = "btrfs" ] || [ "$fstype" = "xfs" ]; then
            fspassno=0
        else
            fspassno=2
        fi
        echo "UUID=$uuid $mntpt $fstype defaults 0 $fspassno" >>"$TARGET_FSTAB"
    done
}

# Copiar sistema base desde el Live ISO (Local Source)
copy_rootfs() {
    echo "Copying system files..."
    # Usamos tar tal cual el original para preservar atributos extendidos
    tar --create --one-file-system --xattrs -f - / 2>/dev/null | \
        tar --extract --xattrs --xattrs-include='*' --preserve-permissions -f - -C "$TARGETDIR"
    
    if [ $? -ne 0 ]; then
        die "Error copying rootfs file system"
    fi

    # Limpieza post-copia live
    rm -f "$TARGETDIR/etc/motd" "$TARGETDIR/etc/issue" "$TARGETDIR/usr/sbin/void-installer"
    # No eliminar sddm.conf porque puede contener config de autologin necesaria
    # Eliminar usuario live del target
    chroot "$TARGETDIR" userdel -r cuerdos >/dev/null 2>&1

    # Aseguramos que el sistema instalado no tenga 'pam_rootok' activado
    PAM_FILES="$TARGETDIR/etc/pam.d/su $TARGETDIR/etc/pam.d/login"
    for file in $PAM_FILES; do
        if [ -f "$file" ]; then
            sed -i 's/^auth\s\+sufficient\s\+pam_rootok\.so/#auth sufficient pam_rootok.so/' "$file"
        fi
    done 
}

# Montar sistemas virtuales para chroot
mount_filesystems() {
    for f in sys proc dev; do
        [ ! -d "$TARGETDIR/$f" ] && mkdir "$TARGETDIR/$f"
        mount --rbind "/$f" "$TARGETDIR/$f"
    done
}

# Desmontar todo al finalizar
umount_filesystems() {
    # Desactivar swap
    local mnts="$(grep -E '^MOUNTPOINT .* swap .*$' "$CONF_FILE" | sort -r -k 5)"
    set -- ${mnts}
    while [ $# -ne 0 ]; do
        local dev=$2; local fstype=$3
        shift 6
        if [ "$fstype" = "swap" ]; then
            swapoff "$dev"
        fi
    done
    # Desmontar recursivamente target
    umount -R "$TARGETDIR"
}

# --- 4. FUNCIONES DE CONFIGURACIÓN DEL SISTEMA ---

set_hostname() {
    local hostname="$(get_option HOSTNAME)"
    echo "${hostname:-void}" > "$TARGETDIR/etc/hostname"
}

set_timezone() {
    local TIMEZONE="$(get_option TIMEZONE)"
    ln -sf "/usr/share/zoneinfo/${TIMEZONE}" "${TARGETDIR}/etc/localtime"
}

set_locale() {
    local LOCALE="$(get_option LOCALE)"
    : "${LOCALE:=C.UTF-8}"
    sed -i -e "s|LANG=.*|LANG=$LOCALE|g" "$TARGETDIR/etc/locale.conf"
    sed -e "/${LOCALE}/s/^\#//" -i "$TARGETDIR/etc/default/libc-locales"
    chroot "$TARGETDIR" xbps-reconfigure -f glibc-locales
}

set_keymap() {
    local KEYMAP="$(get_option KEYMAP)"
    [ -n "$KEYMAP" ] || return 0

    # El identificador procede de un nombre de archivo detectado en la ISO.
    if [[ ! "$KEYMAP" =~ ^[A-Za-z0-9][A-Za-z0-9+._-]*$ ]]; then
        die "Invalid keyboard map: $KEYMAP"
    fi

    # Void Linux aplica el teclado de consola leyendo KEYMAP desde /etc/rc.conf
    install -d "$TARGETDIR/etc"
    touch "$TARGETDIR/etc/rc.conf"
    if grep -Eq '^[[:space:]]*KEYMAP[[:space:]]*=' "$TARGETDIR/etc/rc.conf"; then
        sed -i -E "s|^[[:space:]]*KEYMAP[[:space:]]*=.*$|KEYMAP=$KEYMAP|" "$TARGETDIR/etc/rc.conf"
    else
        printf '\nKEYMAP=%s\n' "$KEYMAP" >> "$TARGETDIR/etc/rc.conf"
    fi

    # Actualizar vconsole.conf solo si la imagen ya lo usa; no crearlo en Void.
    if [ -f "$TARGETDIR/etc/vconsole.conf" ]; then
        if grep -Eq '^[[:space:]]*KEYMAP[[:space:]]*=' "$TARGETDIR/etc/vconsole.conf"; then
            sed -i -E "s|^[[:space:]]*KEYMAP[[:space:]]*=.*$|KEYMAP=$KEYMAP|" "$TARGETDIR/etc/vconsole.conf"
        else
            printf '\nKEYMAP=%s\n' "$KEYMAP" >> "$TARGETDIR/etc/vconsole.conf"
        fi
    fi

    # Xorg/Wayland no interpretan directamente los nombres de mapas de consola.
    local XKB_LAYOUT="$KEYMAP"
    local XKB_VARIANT=""
    case "$KEYMAP" in
        jp106|jp-OADG109A) XKB_LAYOUT="jp" ;;
        kr106|kr) XKB_LAYOUT="kr" ;;
        la-latin1) XKB_LAYOUT="latam" ;;
        es-olpc) XKB_LAYOUT="es"; XKB_VARIANT="olpc" ;;
        es-winkeys) XKB_LAYOUT="es"; XKB_VARIANT="winkeys" ;;
        latam-winkeys) XKB_LAYOUT="latam"; XKB_VARIANT="winkeys" ;;
        fr-afnor) XKB_LAYOUT="fr"; XKB_VARIANT="afnor" ;;
        fr-bepo) XKB_LAYOUT="fr"; XKB_VARIANT="bepo" ;;
        de-mobii) XKB_LAYOUT="de"; XKB_VARIANT="mobii" ;;
        pt-olpc) XKB_LAYOUT="pt"; XKB_VARIANT="olpc" ;;
        jp-winkeys) XKB_LAYOUT="jp"; XKB_VARIANT="winkeys" ;;
        kr-hangul) XKB_LAYOUT="kr"; XKB_VARIANT="hangul" ;;
        kr-winkeys) XKB_LAYOUT="kr"; XKB_VARIANT="winkeys" ;;
        us-winkeys) XKB_LAYOUT="us"; XKB_VARIANT="winkeys" ;;
        uk-winkeys) XKB_LAYOUT="gb"; XKB_VARIANT="winkeys" ;;
        de-winkeys) XKB_LAYOUT="de"; XKB_VARIANT="winkeys" ;;
        fr-winkeys) XKB_LAYOUT="fr"; XKB_VARIANT="winkeys" ;;
        it-winkeys) XKB_LAYOUT="it"; XKB_VARIANT="winkeys" ;;
        pt-winkeys) XKB_LAYOUT="pt"; XKB_VARIANT="winkeys" ;;
        tr-winkeys) XKB_LAYOUT="tr"; XKB_VARIANT="winkeys" ;;
        *-*|*_*) XKB_LAYOUT="${KEYMAP%%[-_]*}" ;;
    esac

    # Xorg
    install -d "$TARGETDIR/etc/X11/xorg.conf.d"
    cat > "$TARGETDIR/etc/X11/xorg.conf.d/00-keyboard.conf" <<EOF
Section "InputClass"
    Identifier "system-keyboard"
    MatchIsKeyboard "on"
    Option "XkbLayout" "$XKB_LAYOUT"
    Option "XkbVariant" "$XKB_VARIANT"
EndSection
EOF

    # Wayland - variables para compositores basados en libxkbcommon/wlroots
    install -d "$TARGETDIR/etc/profile.d" "$TARGETDIR/etc/environment.d"
    cat > "$TARGETDIR/etc/profile.d/kron-keyboard.sh" <<EOF
# Keyboard defaults for Wayland compositors using libxkbcommon/wlroots.
export XKB_DEFAULT_MODEL="pc105"
export XKB_DEFAULT_LAYOUT="$XKB_LAYOUT"
export XKB_DEFAULT_VARIANT="$XKB_VARIANT"
export XKB_DEFAULT_OPTIONS=""
EOF
    chmod 0644 "$TARGETDIR/etc/profile.d/kron-keyboard.sh"

    cat > "$TARGETDIR/etc/environment.d/90-kron-keyboard.conf" <<EOF
XKB_DEFAULT_MODEL=pc105
XKB_DEFAULT_LAYOUT=$XKB_LAYOUT
XKB_DEFAULT_VARIANT=$XKB_VARIANT
XKB_DEFAULT_OPTIONS=
EOF
    chmod 0644 "$TARGETDIR/etc/environment.d/90-kron-keyboard.conf"

    # Display managers pueden iniciar el compositor sin pasar por profile.d
    touch "$TARGETDIR/etc/environment"
    for env_key in XKB_DEFAULT_MODEL XKB_DEFAULT_LAYOUT XKB_DEFAULT_VARIANT XKB_DEFAULT_OPTIONS; do
        case "$env_key" in
            XKB_DEFAULT_MODEL) env_value="pc105" ;;
            XKB_DEFAULT_LAYOUT) env_value="$XKB_LAYOUT" ;;
            XKB_DEFAULT_VARIANT) env_value="$XKB_VARIANT" ;;
            XKB_DEFAULT_OPTIONS) env_value="" ;;
        esac
        if grep -Eq "^[[:space:]]*${env_key}[[:space:]]*=" "$TARGETDIR/etc/environment"; then
            sed -i -E "s|^[[:space:]]*${env_key}[[:space:]]*=.*$|${env_key}=${env_value}|" "$TARGETDIR/etc/environment"
        else
            printf '%s=%s\n' "$env_key" "$env_value" >> "$TARGETDIR/etc/environment"
        fi
    done

    # GNOME/Mutter mantiene el teclado en GSettings y no usa Xorg ni las variables
    install -d "$TARGETDIR/etc/xdg/autostart" "$TARGETDIR/usr/libexec"
    cat > "$TARGETDIR/usr/libexec/kron-wayland-keyboard" <<EOF
#!/bin/sh
# Apply the installer-selected keyboard layout in GNOME Wayland sessions.
command -v gsettings >/dev/null 2>&1 || exit 0
[ "\${XDG_CURRENT_DESKTOP:-}" = "GNOME" ] || exit 0
if [ -n "$XKB_VARIANT" ]; then
    gsettings set org.gnome.desktop.input-sources sources "[('xkb', '${XKB_LAYOUT}+${XKB_VARIANT}')]" || exit 0
else
    gsettings set org.gnome.desktop.input-sources sources "[('xkb', '${XKB_LAYOUT}')]" || exit 0
fi
EOF
    chmod 0755 "$TARGETDIR/usr/libexec/kron-wayland-keyboard"

    cat > "$TARGETDIR/etc/xdg/autostart/kron-wayland-keyboard.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Kron keyboard layout
Comment=Apply the selected keyboard layout in GNOME Wayland
Exec=/usr/libexec/kron-wayland-keyboard
OnlyShowIn=GNOME;
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF
    chmod 0644 "$TARGETDIR/etc/xdg/autostart/kron-wayland-keyboard.desktop"

    # KDE Plasma - kxkbrc en skel para nuevos usuarios
    install -d "$TARGETDIR/etc/skel/.config"
    cat > "$TARGETDIR/etc/skel/.config/kxkbrc" <<EOF
[Layout]
DisplayNames=
LayoutList=$XKB_LAYOUT
Options=
ResetOldOptions=true
SwitchMode=Global
Use=true
VariantList=$XKB_VARIANT
EOF
    chmod 0644 "$TARGETDIR/etc/skel/.config/kxkbrc"
}

set_rootpassword() {
    echo "root:$(get_option ROOTPASSWORD)" | chroot "$TARGETDIR" chpasswd -c SHA512
}

set_useraccount() {
    local USERLOGIN="$(get_option USERLOGIN)"
    if [ -n "$USERLOGIN" ]; then
        chroot "$TARGETDIR" useradd -m -G "$(get_option USERGROUPS)" \
            -c "$(get_option USERNAME)" "$USERLOGIN"
        echo "$USERLOGIN:$(get_option USERPASSWORD)" | \
            chroot "$TARGETDIR" chpasswd -c SHA512
            
        # Sudoers
        if [ -d "$TARGETDIR/etc/sudoers.d" ]; then
            if [[ "$(get_option USERGROUPS)" != *"wheel"* ]]; then
                echo "$USERLOGIN ALL=(ALL:ALL) ALL" > "$TARGETDIR/etc/sudoers.d/$USERLOGIN"
            else
                echo "%wheel ALL=(ALL:ALL) ALL" > "$TARGETDIR/etc/sudoers.d/wheel"
            fi
        fi
    fi
}

# Configura el inicio de sesión automático en el display manager soportado.
set_autologin() {
    local enabled="$(get_option AUTOLOGIN)"
    local manager="$(get_option DISPLAYMANAGER)"
    local userlogin="$(get_option USERLOGIN)"

    [ "$enabled" = "1" ] || return 0

    case "$manager" in
        sddm)
            install -d "$TARGETDIR/etc/sddm.conf.d"
            cat > "$TARGETDIR/etc/sddm.conf.d/10-kron-autologin.conf" <<EOF
[Autologin]
User=$userlogin
Session=default.desktop
Relogin=false
EOF
            ;;
        lightdm)
            install -d "$TARGETDIR/etc/lightdm/lightdm.conf.d"
            cat > "$TARGETDIR/etc/lightdm/lightdm.conf.d/50-kron-autologin.conf" <<EOF
[Seat:*]
autologin-user=$userlogin
autologin-user-timeout=0
EOF
            ;;
        gdm)
            if [ -d "$TARGETDIR/etc/gdm" ]; then
                install -d "$TARGETDIR/etc/gdm"
                target_gdm_config="$TARGETDIR/etc/gdm/custom.conf"
            else
                install -d "$TARGETDIR/etc/gdm3"
                target_gdm_config="$TARGETDIR/etc/gdm3/custom.conf"
            fi
            if [ ! -f "$target_gdm_config" ]; then
                printf '%s\n' "[daemon]" > "$target_gdm_config"
            elif ! grep -q '^\[daemon\]' "$target_gdm_config"; then
                printf '\n%s\n' "[daemon]" >> "$target_gdm_config"
            fi
            if grep -q '^AutomaticLoginEnable=' "$target_gdm_config"; then
                sed -i "s/^AutomaticLoginEnable=.*/AutomaticLoginEnable=true/" "$target_gdm_config"
            else
                sed -i '/^\[daemon\]/a AutomaticLoginEnable=true' "$target_gdm_config"
            fi
            if grep -q '^AutomaticLogin=' "$target_gdm_config"; then
                sed -i "s/^AutomaticLogin=.*/AutomaticLogin=$userlogin/" "$target_gdm_config"
            else
                sed -i "/^AutomaticLoginEnable=/a AutomaticLogin=$userlogin" "$target_gdm_config"
            fi
            ;;
        greetd)
            echo "Autologin no configurado: greetd no es compatible con este instalador."
            ;;
        *)
            echo "Autologin no configurado: no se detectó un display manager compatible."
            ;;
    esac
}

declare -A MIRRORS

# Formato: ["nombre-logico"]="URL"
MIRRORS["Default"]="https://repo-default.voidlinux.org/"
MIRRORS["Finland"]="https://repo-fi.voidlinux.org/"
MIRRORS["Germany"]="https://repo-de.voidlinux.org/"
MIRRORS["Global"]="https://repo-fastly.voidlinux.org/"
MIRRORS["USA"]="https://mirrors.summithq.com/voidlinux/"

set_mirror() {
    local MIRROR_KEY="$(get_option MIRROR)"
    local MIRROR_URL=${MIRRORS[$MIRROR_KEY]}

    # Solo configurar mirror si no es ISO local
    if [[ "$MIRROR_KEY" != "Default" ]] && [[ -n "$MIRROR_URL" ]]; then
        echo "Configuring mirror..."
        log_ui "MIRROR"        
        
        if ! chroot "$TARGETDIR" xmirror -s "$MIRROR_URL"; then
            die "Error configuring mirror $MIRROR_KEY ($MIRROR_URL)"
        fi
        echo "Mirror configured: $MIRROR_KEY ($MIRROR_URL)"
    fi
}

update_system() {
    echo "Downloading system updates..."
    log_ui "UPDATE_DOWNLOAD"

    # Primera fase: descargar al caché, sin instalar todavía.
    if ! chroot "$TARGETDIR" xbps-install -Suy -d; then
        die "Error downloading system updates"
    fi

    echo "Installing downloaded updates..."
    log_ui "UPDATE_INSTALL"
    if ! chroot "$TARGETDIR" xbps-install -uy; then
        die "Error installing system updates"
    fi
    echo "System updated"
}

enable_nonfree_repos() {
    echo "Enabling non-free repositories..."
    log_ui "NON-FREE"

    chroot "$TARGETDIR" xbps-install -Sy void-repo-nonfree || die "Error installing void-repo-nonfree"
    echo "Non-free repositories enabled"
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
        echo "Installing NVIDIA driver: $driver..."
        log_ui "NVIDIA"
        chroot "$TARGETDIR" xbps-install -Sy "$driver" || die "Error installing driver $driver"
        echo "NVIDIA driver successfully installed"
    else
        echo "No compatible NVIDIA driver detected, nouveau/nvk will be used"
    fi
}

install_intel_microcodes() {
    echo "Installing Intel microcode..."
    log_ui "INTEL"
    chroot "$TARGETDIR" xbps-install -Sy intel-ucode || die "Failure when installing Intel microcode"
    echo "Intel microcodes installed correctly"
}

install_extra_software() {
    local update=$(get_option UPDATE)   # checkbox de la GUI
    local nonfree=$(get_option NONFREE)
    local nvidia=$(get_option NVIDIA)
    local intel=$(get_option INTEL)

    if [ "$update" = "1" ]; then
        update_system
        if [ "$nonfree" = "1" ]; then
            enable_nonfree_repos
            if [ "$nvidia" = "1" ]; then
                install_nvidia_driver
            fi

            if [ "$intel" = "1" ]; then
                install_intel_microcodes
            fi
        else
            echo "Non-free repositories and proprietary drivers were not activated"
        fi
    else
        echo "Offline installer: the system will not be updated"
    fi
}

# Instalar GRUB
set_bootloader() {
    local dev="$(get_option BOOTLOADER)" grub_args=""

    if [ "$dev" = "none" ] || [ -z "$dev" ]; then return; fi

    # El branding de GRUB se configura exclusivamente en /etc/default/grub.
    install -d "$TARGETDIR/etc/default"
    if [ -f "$TARGETDIR/etc/default/grub" ]; then
        if grep -q '^GRUB_DISTRIBUTOR=' "$TARGETDIR/etc/default/grub"; then
            sed -i 's|^GRUB_DISTRIBUTOR=.*|GRUB_DISTRIBUTOR="CuerdOS"|' "$TARGETDIR/etc/default/grub"
        else
            printf '\nGRUB_DISTRIBUTOR="CuerdOS"\n' >> "$TARGETDIR/etc/default/grub"
        fi
    else
        printf 'GRUB_DISTRIBUTOR="CuerdOS"\n' > "$TARGETDIR/etc/default/grub"
    fi

    if [ -n "$EFI_SYSTEM" ]; then
        grub_args="--target=$EFI_TARGET --efi-directory=/boot/efi --bootloader-id=CuerdOS --recheck"
    fi

    chroot "$TARGETDIR" grub-install $grub_args "$dev" || die "Error installing GRUB on $dev"
    chroot "$TARGETDIR" grub-mkconfig -o /boot/grub/grub.cfg || die "Error generating grub.cfg"
}

# --- 5. ORQUESTACIÓN PRINCIPAL ---

# Validaciones previas
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root." >&2
    exit 1
fi

if [ ! -f "$CONF_FILE" ]; then
    die "$CONF_FILE was not found. The Python frontend must generate it first."
fi

log_ui "INIT"
echo "Log started at $LOG"

# Paso 1: Discos
log_ui "CREATE_FS"
create_filesystems

# Paso 2: Instalación Base
log_ui "COPY"
copy_rootfs

# Paso 3: Configuración
log_ui "REGIONAL_CONFIG"
mount_filesystems
install -Dm644 "$TARGET_FSTAB" "$TARGETDIR/etc/fstab"
echo "tmpfs /tmp tmpfs defaults,nosuid,nodev 0 0" >> "$TARGETDIR/etc/fstab"
touch "$TARGETDIR/etc/cuerdos-release"

set_keymap
set_locale
set_timezone
set_hostname

# Mirrors y drivers propietarios
set_mirror
install_extra_software

log_ui "USER_CONFIG"
set_rootpassword
set_useraccount
set_autologin

# Paso 4: Bootloader
log_ui "GRUB_INSTALL"
set_bootloader

# Paso 5: Finalizar
chroot "$TARGETDIR" xbps-remove -Ooy kron-installer >/dev/null 2>&1

log_ui "FINISH"
sync
umount_filesystems
rm -f "$TARGET_FSTAB"


log_ui "DONE"

exit 0
