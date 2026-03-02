from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import List, Tuple

import cv2

from utils.io import ensure_dir


def read_yolo_labels(label_path: Path) -> List[Tuple[int, float, float, float, float]]:
    labels: List[Tuple[int, float, float, float, float]] = []
    if not label_path.exists():
        return labels

    for line in label_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            continue
        try:
            cls = int(float(parts[0]))
            cx, cy, w, h = map(float, parts[1:5])
        except Exception:
            continue
        labels.append((cls, cx, cy, w, h))
    return labels


def yolo_to_xyxy(
    cx: float,
    cy: float,
    w: float,
    h: float,
    img_w: int,
    img_h: int,
) -> Tuple[int, int, int, int]:
    x1 = int((cx - w / 2.0) * img_w)
    y1 = int((cy - h / 2.0) * img_h)
    x2 = int((cx + w / 2.0) * img_w)
    y2 = int((cy + h / 2.0) * img_h)

    x1 = max(0, min(img_w - 1, x1))
    y1 = max(0, min(img_h - 1, y1))
    x2 = max(0, min(img_w - 1, x2))
    y2 = max(0, min(img_h - 1, y2))
    return x1, y1, x2, y2


def draw_labels(img_bgr, labels, names):
    for cls, cx, cy, w, h in labels:
        x1, y1, x2, y2 = yolo_to_xyxy(cx, cy, w, h, img_bgr.shape[1], img_bgr.shape[0])
        name = names[cls] if 0 <= cls < len(names) else str(cls)
        color = (0, 255, 0) if name == "person" else (255, 128, 0)
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            img_bgr,
            name,
            (x1, max(0, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )
    return img_bgr


def sample_images(img_dir: Path, n: int, seed: int) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png"}
    paths = [p for p in img_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    rng = random.Random(seed)
    if not paths:
        return []
    if n >= len(paths):
        rng.shuffle(paths)
        return paths
    return rng.sample(paths, n)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sanity-check YOLO labels by drawing boxes on random samples.")
    ap.add_argument("--data-root", type=Path, default=Path("data/yolo"), help="YOLO dataset root")
    ap.add_argument("--splits", type=str, default="train,val", help="Comma-separated splits")
    ap.add_argument("--n", type=int, default=20, help="Images per split")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out-dir", type=Path, default=Path("outputs/images/label_debug"))
    args = ap.parse_args()

    names = ["person", "vehicle"]
    out_dir = ensure_dir(args.out_dir)

    for split in [s.strip() for s in args.splits.split(",") if s.strip()]:
        img_dir = args.data_root / "images" / split
        lbl_dir = args.data_root / "labels" / split
        if not img_dir.exists():
            raise FileNotFoundError(f"Missing images dir: {img_dir}")
        if not lbl_dir.exists():
            raise FileNotFoundError(f"Missing labels dir: {lbl_dir}")

        sampled = sample_images(img_dir, args.n, args.seed)
        split_out = ensure_dir(out_dir / split)

        for img_path in sampled:
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            labels = read_yolo_labels(lbl_path)
            vis = draw_labels(img.copy(), labels, names)
            cv2.imwrite(str(split_out / img_path.name), vis)


if __name__ == "__main__":
    main()
