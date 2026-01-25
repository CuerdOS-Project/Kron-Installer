import os
import subprocess
import json
import glob

class SystemDetector:
    @staticmethod
    def detect_efi():
        """Detecta si el sistema arrancó en modo EFI."""
        return os.path.exists("/sys/firmware/efi")

    @staticmethod
    def detect_disks():
        """
        Retorna una lista de discos usando lsblk en formato JSON.
        Filtra loops y rams.
        """
        try:
            # lsblk -J (JSON), -o (Columnas específicas)
            cmd = ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MODEL,FSTYPE"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            disks = []
            for device in data.get("blockdevices", []):
                if device.get("type") == "disk":
                    disks.append({
                        "name": f"/dev/{device['name']}",
                        "model": device.get("model", "Unknown"),
                        "size": device.get("size"),
                        "children": device.get("children", []) # Particiones
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
        Lista mapas de teclado disponibles en /usr/share/kbd/keymaps
        """
        keymaps = []
        # Búsqueda recursiva básica
        search_path = "/usr/share/kbd/keymaps/**/*.map.gz"
        for filepath in glob.glob(search_path, recursive=True):
            filename = os.path.basename(filepath)
            keymaps.append(filename.replace(".map.gz", ""))
        return sorted(keymaps) or ["es", "us"] # Fallback

    @staticmethod
    def detect_locales():
        """
        Lee /etc/default/libc-locales o lista disponibles.
        Por simplicidad, parseamos el archivo de configuración de Void.
        """
        locales = []
        target = "/etc/default/libc-locales"
        if os.path.exists(target):
            with open(target, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.lstrip("#").split()
                        if parts:
                            locales.append(parts[0])
                
        return sorted(locales)
