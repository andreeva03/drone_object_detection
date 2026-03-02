from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> None:
    ap = argparse.ArgumentParser(prog="aerial-detector", description="Aerial detector (person/vehicle) - train + infer utilities")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_convert = sub.add_parser("convert", help="Convert VisDrone dataset to 2-class YOLO format")
    p_convert.add_argument("--visdrone-root", default="data/visdrone")
    p_convert.add_argument("--out-root", default="data/yolo")
    p_convert.add_argument("--splits", default="train,val")
    p_convert.add_argument("--write-yaml", action="store_true")

    p_train = sub.add_parser("train", help="Train YOLOv8")
    p_train.add_argument("--data", default="data/yolo/data.yaml")
    p_train.add_argument("--model", default="yolov8n.pt")
    p_train.add_argument("--imgsz", default="960")
    p_train.add_argument("--epochs", default="50")
    p_train.add_argument("--batch", default="16")
    p_train.add_argument("--device", default="")
    p_train.add_argument("--project", default="outputs")
    p_train.add_argument("--name", default="train")

    p_infer = sub.add_parser("infer", help="Run inference on images and export annotated images + JSON")
    p_infer.add_argument("--weights", required=True)
    p_infer.add_argument("--source", required=True)
    p_infer.add_argument("--conf", default="0.25")
    p_infer.add_argument("--imgsz", default="960")
    p_infer.add_argument("--out-dir", default="outputs")

    args, _ = ap.parse_known_args()

    if args.cmd == "convert":
        cmd = [sys.executable, "-m", "utils.visdrone_to_yolo"]
        cmd += ["--visdrone-root", args.visdrone_root, "--out-root", args.out_root, "--splits", args.splits]
        if args.write_yaml:
            cmd.append("--write-yaml")
    elif args.cmd == "train":
        cmd = [sys.executable, "train.py"]
        cmd += [
            "--data",
            args.data,
            "--model",
            args.model,
            "--imgsz",
            str(args.imgsz),
            "--epochs",
            str(args.epochs),
            "--batch",
            str(args.batch),
            "--device",
            str(args.device),
            "--project",
            str(args.project),
            "--name",
            str(args.name),
        ]
    else:
        cmd = [sys.executable, "infer.py"]
        cmd += [
            "--weights",
            args.weights,
            "--source",
            args.source,
            "--conf",
            str(args.conf),
            "--imgsz",
            str(args.imgsz),
            "--out-dir",
            str(args.out_dir),
        ]

    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
