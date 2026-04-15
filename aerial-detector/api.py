"""FastAPI backend for VisionDetect AI - connects inference logic to React frontend."""

from __future__ import annotations

import io
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from ultralytics import YOLO

from utils.io import ensure_dir


app = FastAPI(title="VisionDetect AI API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "*",
    ],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_PATH = BASE_DIR / "model" / "best.pt"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

PERSON_CLASS_NAMES = {"person", "pedestrian", "people"}
VEHICLE_CLASS_NAMES = {
    "vehicle",
    "car",
    "van",
    "truck",
    "bus",
    "motor",
    "bicycle",
    "tricycle",
    "awning-tricycle",
}

# Load model on startup
model = None


@app.on_event("startup")
async def startup_event():
    global model
    model_path = MODEL_PATH
    if not model_path.exists():
        fallback_path = BASE_DIR / "yolov8n.pt"
        model_path = fallback_path if fallback_path.exists() else MODEL_PATH
    print(f"Loading model from: {model_path}")
    try:
        model = YOLO(str(model_path))
        print("Model loaded successfully")
        print(f"Model classes: {model.names}")
    except Exception as e:
        print(f"Warning: Could not load model: {e}")
        print("Detection will fail until a valid model is available")


def annotate_image(img_bgr: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    """Draw bounding boxes on image."""
    img_out = img_bgr.copy()
    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        label = det["class"]
        conf = det["confidence"]

        # Color: green for person, orange for vehicle
        color = (
            (0, 255, 0)
            if label == "Person"
            else (255, 128, 0)
            if label == "Vehicle"
            else (128, 128, 128)
        )

        cv2.rectangle(img_out, (x1, y1), (x2, y2), color, 2)
        text = f"{label} {conf:.2f}"
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img_out, (x1, y1 - text_h - 8), (x1 + text_w, y1), color, -1)
        cv2.putText(
            img_out,
            text,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    return img_out


@app.post("/api/detect")
async def detect_image(
    file: UploadFile = File(...), conf: float = Form(0.25), imgsz: int = Form(960)
):
    """Run detection on uploaded image and return results."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server configuration.",
        )

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail=f"Invalid file type. Allowed: JPEG, PNG, WEBP, BMP"
        )

    # Generate unique ID for this detection
    detection_id = str(uuid.uuid4())

    # Save uploaded file
    ext = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    upload_path = UPLOAD_DIR / f"{detection_id}{ext}"

    try:
        contents = await file.read()
        with open(upload_path, "wb") as f:
            f.write(contents)

        # Read image with OpenCV
        img_bgr = cv2.imread(str(upload_path))
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Could not read image file")

        # Run inference
        results = model.predict(source=img_bgr, conf=conf, imgsz=imgsz, verbose=False)
        r0 = results[0]

        # Process detections
        detections: List[Dict[str, Any]] = []
        summary = {"person": 0, "vehicle": 0, "total": 0}

        if r0.boxes is not None and len(r0.boxes) > 0:
            for i, b in enumerate(r0.boxes):
                cls_id = int(b.cls.item())
                confidence = float(b.conf.item())
                x1, y1, x2, y2 = [float(x) for x in b.xyxy.squeeze().tolist()]

                class_name = model.names.get(cls_id, str(cls_id)).lower()

                # Map VisDrone and YOLO classes into the app categories
                if class_name in PERSON_CLASS_NAMES:
                    class_label = "Person"
                    summary["person"] += 1
                elif class_name in VEHICLE_CLASS_NAMES:
                    class_label = "Vehicle"
                    summary["vehicle"] += 1
                else:
                    class_label = class_name.title()

                detections.append(
                    {
                        "id": f"{detection_id}_{i}",
                        "class": class_label,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2],
                    }
                )
                summary["total"] += 1

        # Create annotated image
        annotated_img = annotate_image(img_bgr, detections)
        annotated_path = OUTPUT_DIR / f"{detection_id}_annotated.jpg"
        cv2.imwrite(str(annotated_path), annotated_img)

        # Build response matching frontend types
        response = {
            "id": detection_id,
            "timestamp": str(uuid.uuid4()),  # TODO: use actual timestamp
            "originalImageUrl": f"/api/images/original/{detection_id}{ext}",
            "annotatedImageUrl": f"/api/images/annotated/{detection_id}_annotated.jpg",
            "summary": summary,
            "detections": detections,
        }

        # Save result metadata for history
        result_meta_path = OUTPUT_DIR / f"{detection_id}_result.json"
        with open(result_meta_path, "w") as f:
            json.dump(response, f, indent=2)

        return response

    except Exception as e:
        # Cleanup on error
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/api/images/original/{filename}")
async def get_original_image(filename: str):
    """Serve original uploaded images."""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


@app.get("/api/images/annotated/{filename}")
async def get_annotated_image(filename: str):
    """Serve annotated images with bounding boxes."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Annotated image not found")
    return FileResponse(file_path)


def normalize_result_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert old format results to new format with VisDrone labels."""
    # If already in new format, return as-is
    if isinstance(data.get("summary"), dict) and "classes" in data["summary"]:
        return data
    
    # Convert old format (person/vehicle counts) to new format (classes dict)
    if isinstance(data.get("summary"), dict) and ("person" in data["summary"] or "vehicle" in data["summary"]):
        # Recount detections by class to get accurate class dict
        class_counts: Dict[str, int] = {}
        for det in data.get("detections", []):
            cls = det.get("class", "Other")
            class_counts[cls] = class_counts.get(cls, 0) + 1
        
        total = len(data.get("detections", []))
        data["summary"] = {
            "total": total,
            "classes": class_counts,
        }
    
    return data


@app.get("/api/history")
async def get_history():
    """Get detection history (list of past results)."""
    history = []

    # Find all result metadata files
    for result_file in sorted(OUTPUT_DIR.glob("*_result.json"), reverse=True):
        try:
            with open(result_file) as f:
                data = json.load(f)
                data = normalize_result_format(data)
                # Return minimal data for list view
                history.append(
                    {
                        "id": data["id"],
                        "timestamp": data["timestamp"],
                        "thumbnailUrl": data["annotatedImageUrl"],
                        "summary": data["summary"],
                    }
                )
        except Exception as e:
            print(f"Error loading history item {result_file}: {e}")
            continue

    print(f"History endpoint returning {len(history)} items")
    return history


@app.get("/api/results/{detection_id}")
async def get_result(detection_id: str):
    """Get full result details by ID."""
    result_path = OUTPUT_DIR / f"{detection_id}_result.json"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result not found")

    with open(result_path) as f:
        data = json.load(f)
        data = normalize_result_format(data)
        return data


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_path": getattr(model, "ckpt_path", "unknown") if model else None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
