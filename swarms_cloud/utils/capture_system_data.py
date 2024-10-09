import platform
import socket
import psutil
import uuid
from loguru import logger
from typing import Dict
import requests


def capture_system_data() -> Dict[str, str]:
    """
    Captures extensive system data including platform information, user ID, IP address, CPU count,
    memory information, and other system details.

    Returns:
        Dict[str, str]: A dictionary containing system data.
    """
    try:
        system_data = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_total": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
            "user_id": str(uuid.uuid4()),  # Unique user identifier
            "machine_type": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
        }

        # Get external IP address
        try:
            system_data["external_ip"] = requests.get("https://api.ipify.org").text
        except Exception as e:
            logger.warning("Failed to retrieve external IP: {}", e)
            system_data["external_ip"] = "N/A"

        return system_data
    except Exception as e:
        logger.error("Failed to capture system data: {}", e)
        return {}
