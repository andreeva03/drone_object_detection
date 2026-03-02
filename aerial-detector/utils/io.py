from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path: str | Path, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path: str | Path) -> Any:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: str | Path, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def list_images(path: str | Path) -> list[Path]:
    p = Path(path)
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    if p.is_file() and p.suffix.lower() in exts:
        return [p]
    if not p.exists():
        raise FileNotFoundError(str(p))
    if not p.is_dir():
        raise ValueError(f"Not a file or directory: {p}")

    imgs: list[Path] = []
    for ext in exts:
        imgs.extend(p.rglob(f"*{ext}"))
        imgs.extend(p.rglob(f"*{ext.upper()}"))
    # stable order
    return sorted(set(imgs))


def merge_counts(items: list[Dict[str, Any]], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for it in items:
        k = str(it.get(key))
        out[k] = out.get(k, 0) + 1
    return out
