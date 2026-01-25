from PySide6.QtCore import QThread, Signal
import subprocess
import os

class InstallWorker(QThread):
    # Señales para comunicar con la UI
    progress_update = Signal(int)       # Porcentaje 0-100
    status_update = Signal(str)         # Mensaje corto (Label)
    log_update = Signal(str)            # Mensaje detallado (Terminal)
    finished_success = Signal()         # Fin exitoso
    finished_error = Signal(str)        # Fin con error

    def __init__(self, config_data):
        super().__init__()
        self.config_data = config_data
        self.conf_file = "/tmp/.void-installer.conf"
        self.backend_script = os.path.abspath("backend_install.sh") 

    def generate_conf_file(self):
        """Genera el archivo .conf que espera el backend bash."""
        try:
            with open(self.conf_file, "w") as f:
                # Escribir opciones simples
                for key, value in self.config_data.items():
                    if key != "PARTITIONS": # Las particiones se tratan especial
                        f.write(f"{key} {value}\n")
                
                # Escribir particiones con el formato exacto del backend:
                # MOUNTPOINT dev fstype size mountpoint mkfs_flag
                # Nota: 'size' es dummy aquí porque el backend lo recalcula o ignora para montar
                partitions = self.config_data.get("PARTITIONS", [])
                for part in partitions:
                    # Ejemplo: part = {'dev': '/dev/sda1', 'point': '/', 'fs': 'ext4', 'format': '1'}
                    line = f"MOUNTPOINT {part['dev']} {part['fs']} 0G {part['point']} {part['format']}\n"
                    f.write(line)
            return True
        except Exception as e:
            self.finished_error.emit(f"Error escribiendo config: {e}")
            return False

    def run(self):
        # 1. Generar configuración
        self.status_update.emit("Generando configuración...")
        if not self.generate_conf_file():
            return

        # 2. Ejecutar Backend
        cmd = ["pkexec", "bash", self.backend_script]
        
        try:
            # Popen permite leer stdout línea por línea en tiempo real
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1 # Line buffered
            )

            # Leer salida
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    clean_line = line.strip()
                    # Detectar mensajes de control ">>>" del backend
                    if clean_line.startswith(">>>"):
                        msg = clean_line.replace(">>>", "").strip()
                        self.status_update.emit(msg)
                        self.log_update.emit(f"[INFO] {msg}")
                        
                        # Heurística simple para barra de progreso basada en mensajes clave
                        if "Iniciando" in msg: self.progress_update.emit(5)
                        elif "discos" in msg: self.progress_update.emit(15)
                        elif "Copiando" in msg or "Descargando" in msg: self.progress_update.emit(30)
                        elif "Configurando sistema" in msg: self.progress_update.emit(60)
                        elif "usuarios" in msg: self.progress_update.emit(80)
                        elif "Bootloader" in msg: self.progress_update.emit(90)
                        elif "COMPLETADA" in msg: self.progress_update.emit(100)
                    else:
                        # Log normal (si se escapa algo al stdout)
                        self.log_update.emit(clean_line)

            # Verificar código de salida
            rc = process.poll()
            if rc == 0:
                self.finished_success.emit()
            else:
                err = process.stderr.read()
                self.finished_error.emit(f"El instalador falló (Código {rc}).\n{err}")

        except Exception as e:
            self.finished_error.emit(f"Error crítico ejecutando backend: {e}")
