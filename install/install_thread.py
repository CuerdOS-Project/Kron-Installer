from PySide6.QtCore import QThread, Signal
import subprocess
import os
import time


class InstallWorker(QThread):
    # Señales para comunicar con la UI
    progress_update = Signal(int)       # Porcentaje GLOBAL 0-100 (monótono)
    status_update = Signal(str)         # Token de fase (texto para el label)
    phase_changed = Signal(int, int)    # (fase actual, total de fases)
    mode_changed = Signal(bool)         # True: barra indeterminada (fase sin %)
    log_update = Signal(str)            # Mensaje detallado (Terminal)
    finished_success = Signal()         # Fin exitoso
    finished_error = Signal(str)        # Fin con error

    # Fases del progreso global: token -> (inicio, fin, tipo).
    # El backend emite el token al comenzar cada fase; el trabajo se
    # refleja entre ese token y el siguiente.
    # instant: progreso fijo; copy: porcentaje real; indeterminate: sin porcentaje disponible.
    _PHASES = {
        "INIT":            (0, 2, "instant"),
        "CREATE_FS":       (2, 8, "instant"),
        "COPY":            (8, 70, "copy"),
        "REGIONAL_CONFIG": (70, 73, "instant"),
        "MIRROR":          (73, 74, "instant"),
        "UPDATE_DOWNLOAD": (74, 84, "indeterminate"),
        "UPDATE_INSTALL":  (84, 88, "indeterminate"),
        "NVIDIA":          (88, 89, "indeterminate"),
        "INTEL":           (89, 90, "indeterminate"),
        "USER_CONFIG":     (90, 94, "instant"),
        "GRUB_INSTALL":    (94, 99, "instant"),   # alias histórico del backend
        "BOOTLOADER":      (94, 99, "instant"),   # nombre real: Limine
        "FINISH":          (99, 100, "instant"),
        "DONE":            (100, 100, "instant"),
    }

    # Agrupación de fases para el contador "Fase X de Y" del label.
    _PHASE_GROUP = {
        "INIT": 1, "CREATE_FS": 1,
        "COPY": 2,
        "REGIONAL_CONFIG": 3, "MIRROR": 3,
        "UPDATE_DOWNLOAD": 4, "UPDATE_INSTALL": 4, "NVIDIA": 4, "INTEL": 4,
        "USER_CONFIG": 5,
        "GRUB_INSTALL": 6, "BOOTLOADER": 6,
        "FINISH": 7, "DONE": 7,
    }

    def __init__(self, config_data, demo=False):
        super().__init__()
        self.config_data = config_data
        self.demo = demo
        self.conf_file = "/tmp/.void-installer.conf"

        # Calcular ruta al backend
        self.backend_script = os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),  # carpeta install/
            "..",  # subida a raíz
            "install",
            "backend_install.sh"
        ))

        # Estado de progreso (monótono: la barra nunca retrocede)
        self._max_progress = -1
        self._current_token = None

        # Total de fases visible en el label: sin actualizaciones la fase 4
        # (UPDATE/NVIDIA/INTEL) no ocurre y el total baja a 6.
        self._total_phases = 7 if (
            self.demo or str(config_data.get("UPDATE", "0")) == "1"
        ) else 6

    # --- Motor de progreso ---

    def _emit_progress(self, value):
        """Emite el porcentaje global clampeado a monótono (nunca retrocede)."""
        value = max(self._max_progress, min(100, int(value)))
        self._max_progress = value
        self.progress_update.emit(value)

    def _emit_copy_pct(self, pct):
        """Mapea el porcentaje de fase COPY (0-99) a su tramo global (8-70)."""
        try:
            pct = min(99, max(0, int(pct)))
        except (TypeError, ValueError):
            return
        start, end, _kind = self._PHASES["COPY"]
        self._emit_progress(start + pct * (end - start) // 100)

    def _handle_status(self, token):
        """Procesa un token de fase emitido por el backend (>>> TOKEN)."""
        self._current_token = token
        phase = self._PHASES.get(token)

        if phase is None:
            # Token desconocido (p.ej. "ERROR: ..."): solo texto; la barra
            # no se mueve para no inventar progreso.
            self.status_update.emit(token)
            self.log_update.emit(f"[INFO] {token}")
            return

        start, _end, kind = phase

        # El modo cambia ANTES que el valor: la UI necesita volver a rango
        # (0,100) para poder aceptar el setValue de la fase determinada.
        self.mode_changed.emit(kind == "indeterminate")
        self._emit_progress(start)

        group = self._PHASE_GROUP.get(token)
        if group is not None:
            self.phase_changed.emit(group, self._total_phases)

        self.status_update.emit(token)
        self.log_update.emit(f"[INFO] {token}")

    def _handle_backend_line(self, clean_line):
        """Clasifica una línea del backend: control (>>>) o log normal."""
        if not clean_line.startswith(">>>"):
            self.log_update.emit(clean_line)
            return

        msg = clean_line[3:].strip()

        # Progreso real de la copia: ">>> COPY 42". Solo se acepta mientras
        # la fase actual es COPY (ignora líneas tardías de checkpoints).
        if msg.startswith("COPY ") and self._current_token == "COPY":
            rest = msg[len("COPY "):].strip()
            if rest.isdigit():
                self._emit_copy_pct(rest)
                return

        self._handle_status(msg)

    # --- Modo demo ---

    def _run_demo(self):
        self.log_update.emit("[DEMO] Modo demo activo: no se realizarán cambios reales.")

        steps = [
            ("INIT", 0.4, None),
            ("CREATE_FS", 0.7, None),
            ("COPY", 0.0, "copy"),          # progreso simulado con checkpoints
            ("REGIONAL_CONFIG", 0.4, None),
            ("UPDATE_DOWNLOAD", 1.4, None),  # ejercita la barra indeterminada
            ("UPDATE_INSTALL", 1.2, None),
            ("USER_CONFIG", 0.4, None),
            ("BOOTLOADER", 0.6, None),
            ("FINISH", 0.3, None),
            ("DONE", 0.2, None),
        ]

        for token, delay, kind in steps:
            if self.isInterruptionRequested():
                return

            self._handle_status(token)

            if kind == "copy":
                # Simula los checkpoints de tar del backend real (>>> COPY n)
                for pct in range(0, 101, 5):
                    if self.isInterruptionRequested():
                        return
                    self._emit_copy_pct(pct)
                    self.log_update.emit(f"[DEMO] Copiado {pct}% del sistema base")
                    time.sleep(0.09)
            else:
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
        self._handle_status("INIT")
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
                    self._handle_backend_line(line.strip())

            # Verificar código de salida
            rc = process.poll()
            if rc == 0:
                self._emit_progress(100)
                self.mode_changed.emit(False)
                self.finished_success.emit()
            else:
                self.mode_changed.emit(False)
                self.finished_error.emit(
                    self.tr("El instalador ha fallado. Mire en /tmp/installation.log.")
                )

        except Exception as e:
            error_msg = self.tr("Error crítico al ejecutar el backend: {e}").format(e = e)
            self.finished_error.emit(error_msg)
