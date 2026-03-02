export interface Detection {
  id: string;
  class: 'Vehicle' | 'Person' | 'Other';
  confidence: number;
  bbox: [number, number, number, number]; // x1, y1, x2, y2
}

export interface DetectionResult {
  id: string;
  timestamp: string;
  originalImageUrl: string;
  annotatedImageUrl: string;
  summary: {
    people: number;
    vehicles: number;
    total: number;
  };
  detections: Detection[];
}

export type ViewState = 'detect' | 'history' | 'settings' | 'results';
