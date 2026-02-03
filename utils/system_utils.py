import os
import subprocess
import json
import glob
from utils.utils_locales import KeymapName

class SystemDetector:
    @staticmethod
    def detect_efi():
        """Detecta si el sistema arrancó en modo EFI."""
        return os.path.exists("/sys/firmware/efi")

    @staticmethod
    def has_internet(timeout=2):
        """
        Comprueba si hay conexión a Internet.
        Devuelve True / False.
        """
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout), "1.1.1.1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def detect_disks():
        """
        Retorna una lista de discos usando lsblk en formato JSON.
        Filtra loops, rams y discos sin tamaño o modelo válido.
        """
        try:
            cmd = ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MODEL,FSTYPE"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            disks = []
            for device in data.get("blockdevices", []):
                if device.get("type") != "disk":
                    continue
                model = device.get("model")
                size = device.get("size")
                name = device.get("name", "")
                if not model:
                    model = "Virtual / Generic Disk"
                if name.startswith("zram"):
                    continue
                disks.append({
                    "name": f"/dev/{device['name']}",
                    "model": model,
                    "size": size,
                    "children": device.get("children", [])
                })
            return disks
        except Exception as e:
            print(f"Error detectando discos: {e}")
            return []

    @staticmethod
    def get_flat_partitions():
        """
        Retorna una lista plana de todas las particiones disponibles en el sistema.
        Útil para llenar los ComboBoxes.
        """
        partitions = []
        disks = SystemDetector.detect_disks()
        for disk in disks:
            for part in disk.get("children", []):
                if part.get("type") == "part":
                    partitions.append(f"/dev/{part['name']} ({part['size']})")
        return partitions

    @staticmethod
    def detect_timezones():
        """
        Escanea /usr/share/zoneinfo para obtener Regiones y Ciudades.
        Retorna un diccionario {Region: [Ciudades]}.
        """
        base_dir = "/usr/share/zoneinfo"
        zones = {}
        ignore = ["posix", "right", "Etc", "SystemV"]

        if not os.path.exists(base_dir):
            return {"UTC": ["UTC"]}

        for region in os.listdir(base_dir):
            region_path = os.path.join(base_dir, region)
            if os.path.isdir(region_path) and region not in ignore:
                cities = []
                for city in os.listdir(region_path):
                    # Filtrar solo archivos binarios de zona
                    if os.path.isfile(os.path.join(region_path, city)):
                        cities.append(city)
                if cities:
                    zones[region] = sorted(cities)
        return zones

    @staticmethod
    def detect_keymaps():
        """
        Lista keymaps disponibles y los filtra según nuestra función KeymapName.
        Devuelve la lista filtrada y ordenada.
        """
        search_path = "/usr/share/kbd/keymaps/**/*.map.gz"
        found = []
        for filepath in glob.glob(search_path, recursive=True):
            filename = os.path.basename(filepath).replace(".map.gz", "")
            found.append(filename)

        # Filtrar solo los que KeymapName devuelve distinto del propio código
        filtered = [k for k in found if KeymapName(k) != k]

        return sorted(filtered)

    @staticmethod
    def detect_locales():
        """
        Lee /etc/default/libc-locales ignorando las 10 primeras líneas,
        y devuelve solo locales UTF-8.
        """
        locales = []
        target = "/etc/default/libc-locales"
        if os.path.exists(target):
            with open(target, "r") as f:
                # Saltar las 10 primeras líneas
                for _ in range(10):
                    next(f, None)

                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Quitar comentarios al inicio de línea
                    parts = line.lstrip("#").split()
                    if parts and parts[0].endswith("UTF-8"):
                        locales.append(parts[0])

        return sorted(locales)
