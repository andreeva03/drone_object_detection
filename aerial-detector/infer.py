from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import cv2
from ultralytics import YOLO

from utils.io import ensure_dir, list_images, write_json


def annotate_image(img_bgr, detections: List[Dict[str, Any]]):
    for det in detections:
        x1, y1, x2, y2 = map(int, det["xyxy"])
        label = det["label"]
        conf = det["confidence"]
        cls_name = det["class_name"]
        color = (0, 255, 0) if cls_name == "person" else (255, 128, 0)
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            img_bgr,
            f"{label} {conf:.2f}",
            (x1, max(0, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )
    return img_bgr


def main() -> None:
    ap = argparse.ArgumentParser(description="Run inference on images and export annotated images + JSON + summary counts.")
    ap.add_argument("--weights", type=str, required=True, help="Path to YOLO weights (.pt)")
    ap.add_argument("--source", type=str, required=True, help="Image file or directory")
    ap.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    ap.add_argument("--imgsz", type=int, default=960, help="Inference image size")
    ap.add_argument("--out-dir", type=str, default="outputs", help="Output root")
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    out_images = ensure_dir(out_root / "images")
    out_reports = ensure_dir(out_root / "reports")

    model = YOLO(args.weights)

    img_paths = list_images(args.source)
    all_results: List[Dict[str, Any]] = []
    summary = {"person": 0, "vehicle": 0}

    for img_path in img_paths:
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            continue

        results = model.predict(source=img_bgr, conf=args.conf, imgsz=args.imgsz, verbose=False)
        r0 = results[0]

        detections: List[Dict[str, Any]] = []
        if r0.boxes is not None and len(r0.boxes) > 0:
            for b in r0.boxes:
                cls_id = int(b.cls.item())
                conf = float(b.conf.item())
                x1, y1, x2, y2 = [float(x) for x in b.xyxy.squeeze().tolist()]
                class_name = model.names.get(cls_id, str(cls_id))
                label = "person" if class_name == "person" else ("vehicle" if class_name == "vehicle" else class_name)

                det = {
                    "class_id": cls_id,
                    "class_name": class_name,
                    "label": label,
                    "confidence": conf,
                    "xyxy": [x1, y1, x2, y2],
                }
                detections.append(det)

                if label in summary:
                    summary[label] += 1

        annotated = annotate_image(img_bgr.copy(), detections)
        out_img_path = out_images / img_path.name
        cv2.imwrite(str(out_img_path), annotated)

        per_image = {
            "image": str(img_path),
            "output_image": str(out_img_path),
            "detections": detections,
            "counts": {
                "person": sum(1 for d in detections if d["label"] == "person"),
                "vehicle": sum(1 for d in detections if d["label"] == "vehicle"),
            },
        }
        all_results.append(per_image)

        write_json(out_reports / f"{img_path.stem}.json", per_image)

    final_report = {
        "source": args.source,
        "weights": args.weights,
        "num_images": len(all_results),
        "summary_counts": summary,
        "images": all_results,
    }
    write_json(out_root / "results.json", final_report)


if __name__ == "__main__":
    main()
