# VisionDetect AI - Frontend Integration

This guide explains how to connect the React frontend (`ui/visiondetect-ai`) to the YOLO-based aerial detection backend.

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│  React Frontend     │         │  FastAPI Backend    │
│  (Port 5173)        │◄───────►│  (Port 8000)        │
│                     │  CORS   │                     │
│ - Upload images     │         │ - YOLO inference    │
│ - Display results   │         │ - Image annotation  │
│ - Download JSON     │         │ - Serve images      │
└─────────────────────┘         └─────────────────────┘
```

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd aerial-detector
pip install -r requirements.txt
```

**Frontend:**
```bash
cd ui/visiondetect-ai
npm install
```

### 2. Start the Backend Server

```bash
cd aerial-detector
python api.py
```

The API will start on `http://localhost:8000`

You can verify it's running by visiting:
- `http://localhost:8000/api/health` - Health check endpoint
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)

### 3. Start the Frontend

In a new terminal:
```bash
cd ui/visiondetect-ai
npm run dev
```

The frontend will start on `http://localhost:5173`

### 4. Test the Integration

1. Open `http://localhost:5173` in your browser
2. Upload an aerial image (JPG or PNG)
3. Click "Start Detection"
4. View the detection results with bounding boxes
5. Download the JSON data if needed

## API Endpoints

### `POST /api/detect`
Upload an image and run object detection.

**Request:**
- `file`: Image file (multipart/form-data)
- `conf`: Confidence threshold (default: 0.25)
- `imgsz`: Image size for inference (default: 960)

**Response:**
```json
{
  "id": "uuid",
  "timestamp": "ISO date",
  "originalImageUrl": "/api/images/original/...",
  "annotatedImageUrl": "/api/images/annotated/...",
  "summary": {
    "people": 5,
    "vehicles": 10,
    "total": 15
  },
  "detections": [
    {
      "id": "uuid_0",
      "class": "Vehicle",
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2]
    }
  ]
}
```

### `GET /api/images/original/{filename}`
Serve original uploaded images.

### `GET /api/images/annotated/{filename}`
Serve images with bounding boxes drawn.

### `GET /api/history`
Get list of past detections.

### `GET /api/health`
Health check endpoint.

## Configuration

### Backend Environment Variables

Create a `.env` file in `aerial-detector/`:

```env
# Model path (defaults to outputs/train/weights/best.pt or yolov8n.pt)
MODEL_PATH=outputs/train/weights/best.pt

# Upload and output directories
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
```

### Frontend Environment Variables

Create a `.env` file in `ui/visiondetect-ai/`:

```env
# API URL - change this if your backend runs on a different port/host
VITE_API_URL=http://localhost:8000
```

## Files Modified/Created

### New Backend File
- `aerial-detector/api.py` - FastAPI application wrapping the inference logic

### Updated Frontend Files
- `aerial-detector/ui/visiondetect-ai/src/App.tsx` - Updated to:
  - Handle real file uploads
  - Call the `/api/detect` endpoint
  - Display actual detection results
  - Support drag-and-drop
  - Show upload preview
  - Download JSON results

### Updated Dependencies
- `aerial-detector/requirements.txt` - Added fastapi, uvicorn, python-multipart
- `aerial-detector/ui/visiondetect-ai/.env.example` - Added VITE_API_URL

## Features

### What's Connected
✅ Image upload with drag-and-drop support  
✅ Real-time object detection via API  
✅ Bounding box visualization on annotated images  
✅ Detection summary (people, vehicles, total)  
✅ Detailed detection list with confidence scores  
✅ JSON download of results  
✅ Error handling and loading states  

### What's Still Mock
⚠️ History view (uses placeholder data)  
⚠️ Settings page (UI only)  

## Troubleshooting

### "Model not loaded" error
The backend tries to load `outputs/train/weights/best.pt` first, then falls back to `yolov8n.pt`. Make sure one of these exists, or set `MODEL_PATH` environment variable.

### CORS errors
If you see CORS errors in the browser console, make sure the backend is running and the frontend is connecting to the correct URL (check `VITE_API_URL` in your `.env` file).

### Port conflicts
- Backend defaults to port 8000
- Frontend defaults to port 5173

Change these in the startup commands if needed:
```bash
# Backend on different port
python api.py  # Edit the port at the bottom of api.py

# Frontend on different port
npm run dev -- --port 3000
```

## Next Steps

To fully implement the remaining features:

1. **History**: Connect to `/api/history` endpoint to fetch real past detections
2. **Settings**: Add backend endpoints to save/load user preferences
3. **Authentication**: Add user management if needed
4. **Batch Processing**: Extend API to handle multiple images
5. **Training**: Add endpoint to trigger model training

## Production Deployment

For production:

1. Set up a production WSGI server for the backend (e.g., gunicorn)
2. Configure environment variables for production
3. Set up proper static file serving for images
4. Add authentication/authorization
5. Consider using a CDN for serving images
6. Add rate limiting and request validation

Example production backend run:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
```
