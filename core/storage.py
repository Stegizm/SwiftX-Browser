"""
core/storage.py
JSON tabanlı kalıcı veri okuma/yazma yardımcıları.
"""

import json
import os
from .constants import DATA_DIR


def ensure_data_dir() -> None:
    """Veri klasörünün var olduğunu garantiler."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load(path: str, default):
    """JSON dosyasını yükle; hata olursa default döndür."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(path: str, data) -> None:
    """Veriyi JSON dosyasına yaz."""
    ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
