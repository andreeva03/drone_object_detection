from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    ap = argparse.ArgumentParser(description="Train YOLOv8 on 2-class (person/vehicle) dataset.")
    ap.add_argument("--data", type=str, default="data/yolo/data.yaml", help="Path to data.yaml")
    ap.add_argument("--model", type=str, default="yolov8n.pt", help="Base model (e.g., yolov8n.pt)")
    ap.add_argument("--imgsz", type=int, default=960)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", type=str, default="", help="CUDA device id, 'cpu', or empty for auto")
    ap.add_argument("--project", type=str, default="outputs")
    ap.add_argument("--name", type=str, default="train")
    args = ap.parse_args()

    model = YOLO(args.model)

    results = model.train(
        data=args.data,
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device if args.device else None,
        project=args.project,
        name=args.name,
    )

    # Ultralytics saves best.pt/last.pt under {project}/{name}/weights
    out_dir = Path(args.project) / args.name
    print(f"Training complete. Outputs in: {out_dir}")


if __name__ == "__main__":
    main()
