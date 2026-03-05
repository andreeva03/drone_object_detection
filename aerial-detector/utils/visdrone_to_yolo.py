from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from tqdm import tqdm

# VisDrone detection categories (common):
# 0 ignored regions
# 1 pedestrian
# 2 people
# 3 bicycle
# 4 car
# 5 van
# 6 truck
# 7 tricycle
# 8 awning-tricycle
# 9 bus
# 10 motor
# 11 others
#
# MVP mapping:
# person  = {1,2}
# vehicle = {4,5,6,9}

PERSON_IDS = {1, 2}
VEHICLE_IDS = {4, 5, 6, 9}
IGNORED_IDS = {0}


@dataclass(frozen=True)
class YoloBox:
    cls: int
    cx: float
    cy: float
    w: float
    h: float

    def to_line(self) -> str:
        return f"{self.cls} {self.cx:.6f} {self.cy:.6f} {self.w:.6f} {self.h:.6f}"


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def visdrone_row_to_yolo(row: str, img_w: int, img_h: int) -> YoloBox | None:
    """Parse one VisDrone annotation row and map to 2-class YOLO.

    Row format: x,y,w,h,score,category,truncation,occlusion
    - skipped if category is ignored/unknown
    - filters invalid boxes (w<=0 or h<=0)
    """

    parts = row.strip().split(",")
    if len(parts) < 8:
        return None

    try:
        x, y, w, h = map(float, parts[0:4])
        cat = int(float(parts[5]))
    except Exception:
        return None

    if cat in IGNORED_IDS:
        return None

    if w <= 0 or h <= 0:
        return None

    if cat in PERSON_IDS:
        cls = 0
    elif cat in VEHICLE_IDS:
        cls = 1
    else:
        return None

    cx = (x + w / 2.0) / float(img_w)
    cy = (y + h / 2.0) / float(img_h)
    nw = w / float(img_w)
    nh = h / float(img_h)

    return YoloBox(cls=cls, cx=_clamp01(cx), cy=_clamp01(cy), w=_clamp01(nw), h=_clamp01(nh))


def convert_split(visdrone_root: Path, out_root: Path, split: str) -> None:
    """Convert one VisDrone split into YOLO layout:

    out_root/
      images/{split}/*.jpg
      labels/{split}/*.txt
    """

    img_dir = visdrone_root / split / "images"
    ann_dir = visdrone_root / split / "annotations"

    if not img_dir.exists():
        raise FileNotFoundError(f"Missing images dir: {img_dir}")
    if not ann_dir.exists():
        raise FileNotFoundError(f"Missing annotations dir: {ann_dir}")

    out_img_dir = out_root / "images" / split
    out_lbl_dir = out_root / "labels" / split
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_lbl_dir.mkdir(parents=True, exist_ok=True)

    img_paths = sorted([p for p in img_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])

    for img_path in tqdm(img_paths, desc=f"convert:{split}"):
        stem = img_path.stem
        ann_path = ann_dir / f"{stem}.txt"

        # copy image (hardlink if possible)
        out_img = out_img_dir / img_path.name
        if not out_img.exists():
            try:
                out_img.hardlink_to(img_path)
            except Exception:
                out_img.write_bytes(img_path.read_bytes())

        # if missing ann, write empty label
        if not ann_path.exists():
            (out_lbl_dir / f"{stem}.txt").write_text("", encoding="utf-8")
            continue

        with Image.open(img_path) as im:
            img_w, img_h = im.size

        yolo_lines: list[str] = []
        for row in ann_path.read_text(encoding="utf-8").splitlines():
            box = visdrone_row_to_yolo(row, img_w, img_h)
            if box is None:
                continue
            yolo_lines.append(box.to_line())

        (out_lbl_dir / f"{stem}.txt").write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8")


def write_data_yaml(out_root: Path, yaml_path: Path) -> None:
    # Ultralytics YOLO data.yaml
    # Required by user:
    # path: data/yolo
    # train: images/train
    # val: images/val
    # names: ["person","vehicle"]
    content = """path: {root}
train: images/train
val: images/val

names: ["person", "vehicle"]
""".format(root=str(out_root).replace("\\", "/"))

    yaml_path.write_text(content, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert VisDrone annotations to 2-class YOLO dataset (person/vehicle).")
    ap.add_argument("--visdrone-root", type=Path, default=Path("data/visdrone"), help="Root containing VisDrone splits.")
    ap.add_argument("--out-root", type=Path, default=Path("data/yolo"), help="Output YOLO dataset root.")
    ap.add_argument("--splits", type=str, default="train,val", help="Comma-separated splits to convert (e.g. train,val,test).")
    ap.add_argument("--write-yaml", action="store_true", help="Write data.yaml in out-root.")
    args = ap.parse_args()

    for split in [s.strip() for s in args.splits.split(",") if s.strip()]:
        convert_split(args.visdrone_root, args.out_root, split)

    if args.write_yaml:
        write_data_yaml(args.out_root, args.out_root / "data.yaml")


if __name__ == "__main__":
    main()
