from PySide6.QtCore import QThread, Signal
import subprocess
import os
import threading
import time

class InstallWorker(QThread):
    # Señales para comunicar con la UI
    progress_update = Signal(int)       # Porcentaje 0-100
    status_update = Signal(str)         # Mensaje corto (Label)
    log_update = Signal(str)            # Mensaje detallado (Terminal)
    finished_success = Signal()         # Fin exitoso
    finished_error = Signal(str)        # Fin con error

    def __init__(self, config_data, demo=False):
        super().__init__()
        self.config_data = config_data
        self.demo = demo
        self.conf_file = "/tmp/.void-installer.conf"

        # Calcular ruta al backend
        self.backend_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),  # carpeta install/
            "..",  # subida a raíz
            "install",
            "backend_install.sh"
        )
        self.backend_script = os.path.abspath(self.backend_script) 

        # Variables para controlar la animación del progreso
        self._progress_thread = None
        self._stop_progress_event = threading.Event()

    def _scaling_task(self, start_val, end_val):
        """
        Función que se ejecuta en un hilo separado para incrementar la barra.
        """
        current = start_val
        while not self._stop_progress_event.is_set() and current < end_val:
            current += 1
            
            if current > end_val:
                current = end_val
            
            self.progress_update.emit(int(current))
            
            time.sleep(10)

    def _stop_scaling(self):
        """Detiene el hilo de progreso actual si existe."""
        if self._progress_thread and self._progress_thread.is_alive():
            self._stop_progress_event.set()
            self._progress_thread.join(timeout=1)

    def _start_scaling(self, start_val, end_val):
        """Inicia el hilo de progreso."""
        # Parar y reiniciar hilo
        self._stop_scaling()
        self._stop_progress_event.clear()
        
        # Crear e iniciar nuevo hilo
        self._progress_thread = threading.Thread(
            target=self._scaling_task,
            args=(start_val, end_val),
            daemon=True
        )
        self._progress_thread.start()

    def _run_demo(self):
        """
        Simulacion para desarrolladores (--demo): reproduce la secuencia
        de estados y el avance de la barra de progreso sin ejecutar el
        backend real, sin pkexec y sin tocar discos ni archivos del sistema.
        """
        steps = [
            ("INIT", 5, 0.4),
            ("CREATE_FS", 15, 0.4),
            ("COPY", 45, 1.2),
            ("REGIONAL_CONFIG", 55, 0.4),
            ("UPDATE", 65, 1.0),
            ("USER_CONFIG", 85, 0.4),
            ("GRUB_INSTALL", 95, 0.4),
            ("DONE", 100, 0.2),
        ]

        self.log_update.emit("[DEMO] Modo demo activo: no se realizarán cambios reales.")

        for token, value, delay in steps:
            if self.isInterruptionRequested():
                return
            self.status_update.emit(token)
            self.log_update.emit(f"[DEMO] Simulando paso: {token}")
            self.progress_update.emit(value)
            time.sleep(delay)

        self.finished_success.emit()

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
            error_msg = self.tr("Error al escribir la configuración: {e}").format(e = e)
            self.finished_error.emit(error_msg)
            return False

    def run(self):
        if self.demo:
            self._run_demo()
            return

        # 1. Generar configuracion
        self.status_update.emit("INIT")
        if not self.generate_conf_file():
            return

        # 2. Ejecutar Backend
        cmd = ["pkexec", "bash", self.backend_script]
        
        try:
            # Popen permite leer stdout línea por línea en tiempo real
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
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
                        
                        # Casos donde queremos animación progresiva
                        if "COPY" in msg:
                            self._start_scaling(30, 49) # Anima entre 30% y 49%
                        
                        elif "UPDATE" in msg:
                            self._start_scaling(50, 69) # Anima entre 50% y 69%
                        
                        # Casos donde paramos animación y fijamos valor exacto
                        elif "INIT" in msg:
                            self._stop_scaling()
                            self.progress_update.emit(5)
                        elif "CREATE_FS" in msg:
                            self._stop_scaling()
                            self.progress_update.emit(15)
                        elif "REGIONAL_CONFIG" in msg:
                            self._stop_scaling()
                            self.progress_update.emit(50)
                        elif "USER_CONFIG" in msg:
                            self._stop_scaling()
                            self.progress_update.emit(85)
                        elif "GRUB_INSTALL" in msg:
                            self._stop_scaling()
                            self.progress_update.emit(90)
                        elif "DONE" in msg:
                            self._stop_scaling()
                            self.progress_update.emit(100)
                            
                    else:
                        self.log_update.emit(clean_line)

            # Verificar código de salida
            self._stop_scaling()

            rc = process.poll()
            if rc == 0:
                self.finished_success.emit()
            else:
                self.finished_error.emit(
                    self.tr("El instalador ha fallado. Mire en /tmp/installation.log.")
                )

        except Exception as e:
            self._stop_scaling()

            error_msg = self.tr("Error crítico al ejecutar el backend: {e}").format(e = e)
            self.finished_error.emit(error_msg)