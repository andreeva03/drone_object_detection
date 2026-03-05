# Aerial Detector (MVP)

Inputs: image files (`.jpg`/`.png`, or a folder).

Classes (MVP, 2-class for stability):
- `person`
- `vehicle` (merged: car/van/bus/truck)

Outputs:
- annotated images with boxes + labels + confidence
- per-image JSON results
- summary counts per class

## Repo layout

See:
- [`aerial-detector/app.py`](aerial-detector/app.py)
- [`aerial-detector/train.py`](aerial-detector/train.py)
- [`aerial-detector/infer.py`](aerial-detector/infer.py)
- [`aerial-detector/utils/visdrone_to_yolo.py`](aerial-detector/utils/visdrone_to_yolo.py)

## Setup

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r aerial-detector\requirements.txt
```

## 1) Prepare VisDrone → YOLO (2 classes)

### Manual download (recommended)

Some VisDrone download pages require acceptance/login, so this repo assumes you **manually download** the VisDrone *detection* dataset and then place the extracted folders under `aerial-detector/data/visdrone/`.

Expected layout (per split):
- `aerial-detector/data/visdrone/train/images/` + `aerial-detector/data/visdrone/train/annotations/`
- `aerial-detector/data/visdrone/val/images/` + `aerial-detector/data/visdrone/val/annotations/`
- (optional) `aerial-detector/data/visdrone/test/images/` + `aerial-detector/data/visdrone/test/annotations/`

### Convert

```bat
cd aerial-detector
python -m utils.visdrone_to_yolo --visdrone-root data/visdrone --out-root data/yolo --splits train,val --write-yaml
```

This creates:
- `aerial-detector/data/yolo/train/images + labels`
- `aerial-detector/data/yolo/val/images + labels`
- `aerial-detector/data/yolo/data.yaml`

## 2) Sanity-check labels (required)

Randomly sample N images from train/val, draw YOLO labels, and save to `outputs/images/label_debug/`:

```bat
cd aerial-detector
python -m utils.visualize_labels --data-root data/yolo --splits train,val --n 20 --out-dir outputs\images\label_debug
```

Inspect the saved images before training.

## 3) Train

```bat
cd aerial-detector
python train.py --data data/yolo/data.yaml --model yolov8n.pt --imgsz 960 --epochs 50 --batch 16
```

Weights are written under `aerial-detector/outputs/train/weights/` (e.g. `best.pt`).

## 3) Infer on images

```bat
cd aerial-detector
python infer.py --weights outputs/train/weights/best.pt --source path\to\images --conf 0.25 --imgsz 960 --out-dir outputs
```

Outputs:
- annotated images: `aerial-detector/outputs/images/`
- per-image JSON: `aerial-detector/outputs/reports/<image>.json`
- combined JSON: `aerial-detector/outputs/results.json`

## Optional: single entrypoint

```bat
cd aerial-detector
python app.py convert --visdrone-root data/visdrone --out-root data/yolo --splits train,val --write-yaml
python app.py train --data data/yolo/data.yaml --model yolov8n.pt
python app.py infer --weights outputs/train/weights/best.pt --source path\to\images
```
