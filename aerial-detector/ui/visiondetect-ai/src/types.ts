export interface Detection {
  id: string;
  class: string;
  confidence: number;
  bbox: [number, number, number, number]; // x1, y1, x2, y2
}

export interface DetectionResult {
  id: string;
  timestamp: string;
  originalImageUrl: string;
  annotatedImageUrl: string;
  summary: {
    total: number;
    classes: Record<string, number>;
  };
  detections: Detection[];
}

export type ViewState = 'detect' | 'history' | 'settings' | 'results';
