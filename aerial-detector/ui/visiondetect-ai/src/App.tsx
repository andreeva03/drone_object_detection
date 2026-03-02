import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowLeft, 
  Download, 
  History, 
  Scan, 
  Settings, 
  Users, 
  Car, 
  BarChart3, 
  ExternalLink,
  ChevronRight,
  Upload,
  Loader2,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { DetectionResult, ViewState, Detection } from './types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Mock mode - set to true for UI preview without backend
const USE_MOCK = true;

// Mock Data for demo
const MOCK_RESULT: DetectionResult = {
  id: 'res_123',
  timestamp: new Date().toISOString(),
  originalImageUrl: 'https://images.unsplash.com/photo-1506501139174-099022df5260?auto=format&fit=crop&q=80&w=1000',
  annotatedImageUrl: 'https://images.unsplash.com/photo-1506501139174-099022df5260?auto=format&fit=crop&q=80&w=1000',
  summary: {
    people: 12,
    vehicles: 48,
    total: 60
  },
  detections: [
    { id: '1', class: 'Vehicle', confidence: 0.98, bbox: [124, 45, 210, 88] },
    { id: '2', class: 'Person', confidence: 0.94, bbox: [452, 192, 468, 215] },
    { id: '3', class: 'Vehicle', confidence: 0.91, bbox: [89, 412, 156, 450] },
    { id: '4', class: 'Vehicle', confidence: 0.88, bbox: [312, 55, 380, 92] },
    { id: '5', class: 'Vehicle', confidence: 0.99, bbox: [200, 100, 250, 150] },
    { id: '6', class: 'Person', confidence: 0.87, bbox: [400, 300, 420, 340] },
  ]
};

export default function App() {
  const [view, setView] = useState<ViewState>('detect');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedResult, setSelectedResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.title = "Vision Detect AI";
  }, []);

  const handleDetectionComplete = (result: DetectionResult) => {
    setSelectedResult(result);
    setView('results');
  };

  const renderHeader = () => {
    if (view === 'results') {
      return (
        <header className="flex items-center justify-between px-6 sm:px-8 lg:px-12 py-4 bg-white border-b border-gray-100 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => {
                setView('detect');
                setSelectedResult(null);
                setError(null);
              }}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <ArrowLeft className="w-6 h-6 text-gray-700" />
            </button>
            <h1 className="text-xl font-semibold text-gray-900">Detection Results</h1>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => selectedResult && downloadResults(selectedResult)}
              className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </header>
      );
    }

    return (
      <header className="px-6 sm:px-8 lg:px-12 py-8 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">VisionDetect AI</h1>
            <p className="text-gray-500 mt-1">Intelligent Aerial Analysis</p>
          </div>
          {USE_MOCK && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-bold rounded-full border border-yellow-200">
              DEMO MODE
            </span>
          )}
        </div>
      </header>
    );
  };

  const renderContent = () => {
    switch (view) {
      case 'results':
        return selectedResult ? <ResultsView result={selectedResult} /> : null;
      case 'history':
        return <HistoryView onSelect={(res) => { setSelectedResult(res); setView('results'); }} />;
      case 'settings':
        return <SettingsView />;
      default:
        return (
          <DetectView 
            onDetectionComplete={handleDetectionComplete} 
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
            error={error}
            setError={setError}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
      <div className="flex-1 flex flex-col w-full bg-white shadow-sm overflow-hidden pb-24">
        {renderHeader()}
        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 px-6 py-3 z-20">
        <div className="w-full flex justify-between items-center px-4 sm:px-8 lg:px-16">
          <NavButton 
            active={view === 'history'} 
            onClick={() => setView('history')} 
            icon={<History />} 
            label="History" 
          />
          <NavButton 
            active={view === 'detect' || view === 'results'} 
            onClick={() => setView('detect')} 
            icon={<Scan />} 
            label="Detect" 
          />
          <NavButton 
            active={view === 'settings'} 
            onClick={() => setView('settings')} 
            icon={<Settings />} 
            label="Settings" 
          />
        </div>
      </nav>
    </div>
  );
}

function NavButton({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
  return (
    <button 
      onClick={onClick}
      className={`flex flex-col items-center gap-1 transition-colors ${active ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
    >
      {React.cloneElement(icon as React.ReactElement, { className: 'w-6 h-6' })}
      <span className="text-xs font-medium">{label}</span>
      {active && <motion.div layoutId="nav-indicator" className="w-1 h-1 bg-blue-600 rounded-full mt-0.5" />}
    </button>
  );
}

function DetectView({ 
  onDetectionComplete, 
  isProcessing,
  setIsProcessing,
  error,
  setError
}: { 
  onDetectionComplete: (result: DetectionResult) => void, 
  isProcessing: boolean,
  setIsProcessing: (val: boolean) => void,
  error: string | null,
  setError: (val: string | null) => void
}) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        handleFile(file);
      }
    }
  };

  const handleFile = (file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleStartDetection = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);

    if (USE_MOCK) {
      // Simulate processing with mock data
      setTimeout(() => {
        setIsProcessing(false);
        // Create a mock result with the uploaded image preview
        const mockWithPreview: DetectionResult = {
          ...MOCK_RESULT,
          id: `demo_${Date.now()}`,
          timestamp: new Date().toISOString(),
          originalImageUrl: previewUrl || MOCK_RESULT.originalImageUrl,
          annotatedImageUrl: previewUrl || MOCK_RESULT.annotatedImageUrl,
        };
        onDetectionComplete(mockWithPreview);
      }, 2000);
      return;
    }

    // Real API call
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('conf', '0.25');
    formData.append('imgsz', '960');

    try {
      const response = await fetch(`${API_BASE_URL}/api/detect`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Detection failed');
      }

      const result: DetectionResult = await response.json();
      
      // Convert relative URLs to full URLs
      result.originalImageUrl = `${API_BASE_URL}${result.originalImageUrl}`;
      result.annotatedImageUrl = `${API_BASE_URL}${result.annotatedImageUrl}`;
      
      onDetectionComplete(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsProcessing(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
  };

  return (
    <div className="p-6 sm:p-8 lg:p-12 space-y-6 max-w-7xl mx-auto">
      <div 
        className={`h-48 md:h-56 bg-gray-100 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center p-6 text-center transition-colors overflow-hidden ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
        } ${selectedFile ? 'border-solid' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        {previewUrl ? (
          <div className="relative w-full h-full">
            <img 
              src={previewUrl} 
              alt="Preview" 
              className="w-full h-full object-contain rounded-lg"
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                clearFile();
              }}
              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="absolute bottom-2 left-2 bg-black/50 text-white px-3 py-1 rounded-lg text-sm">
              {selectedFile?.name}
            </div>
          </div>
        ) : (
          <>
            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <Upload className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-gray-900">Upload Aerial Image</h3>
            <p className="text-xs text-gray-500 mt-1">Drag and drop or click to browse files (JPG, PNG)</p>
          </>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">Detection Parameters</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-xs text-gray-500 block mb-1">Confidence Threshold</span>
            <span className="font-mono font-medium">0.25</span>
          </div>
          <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
            <span className="text-xs text-gray-500 block mb-1">Model Version</span>
            <span className="font-mono font-medium">YOLOv8</span>
          </div>
        </div>
      </div>

      <button 
        onClick={handleStartDetection}
        disabled={isProcessing || !selectedFile}
        className="w-full py-4 bg-blue-600 text-white rounded-2xl font-semibold shadow-lg shadow-blue-200 hover:bg-blue-700 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
      >
        {isProcessing ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Processing Image...
          </>
        ) : (
          <>
            <Scan className="w-5 h-5" />
            Start Detection
          </>
        )}
      </button>
    </div>
  );
}

const downloadResults = (result: DetectionResult) => {
  const dataStr = JSON.stringify(result, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
  const exportFileDefaultName = `detection_${result.id}.json`;
  
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
};

function ResultsView({ result }: { result: DetectionResult }) {
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);
  const [lightboxLabel, setLightboxLabel] = useState<string>('');
  const [filterClass, setFilterClass] = useState<string>('All Classes');

  const openLightbox = (imageUrl: string, label: string) => {
    setLightboxImage(imageUrl);
    setLightboxLabel(label);
  };

  const closeLightbox = () => {
    setLightboxImage(null);
    setLightboxLabel('');
  };

  // Filter detections based on selected class
  const filteredDetections = result.detections.filter(det => {
    if (filterClass === 'All Classes') return true;
    if (filterClass === 'Vehicles') return det.class === 'Vehicle';
    if (filterClass === 'People') return det.class === 'Person';
    return true;
  });

  // Calculate filtered counts
  const filteredCounts = {
    people: filteredDetections.filter(d => d.class === 'Person').length,
    vehicles: filteredDetections.filter(d => d.class === 'Vehicle').length,
    total: filteredDetections.length
  };

  return (
    <div className="p-6 sm:p-8 lg:p-12 space-y-6 max-w-7xl mx-auto">
      {/* Lightbox Modal */}
      {lightboxImage && (
        <div 
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={closeLightbox}
        >
          <button
            onClick={closeLightbox}
            className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
          <div className="max-w-5xl max-h-[90vh] w-full flex flex-col items-center">
            <img 
              src={lightboxImage} 
              alt={lightboxLabel}
              className="max-w-full max-h-[85vh] object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
            <p className="text-white mt-4 text-lg font-medium">{lightboxLabel}</p>
          </div>
        </div>
      )}

      {/* Image Comparison */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            Image Comparison
          </h2>
          <a 
            href={result.annotatedImageUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 text-sm font-medium flex items-center gap-1 hover:underline"
          >
            <ExternalLink className="w-4 h-4" />
            Open Annotated
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            className="relative rounded-2xl overflow-hidden shadow-md cursor-pointer hover:shadow-xl transition-shadow"
            onClick={() => openLightbox(result.originalImageUrl, 'Original Image')}
          >
            <img 
              src={result.originalImageUrl} 
              alt="Original" 
              className="w-full h-48 md:h-56 object-cover"
            />
            <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors" />
            <div className="absolute bottom-3 left-3 bg-black/50 backdrop-blur-md text-white px-2 py-1 rounded-lg text-xs font-medium">
              Original
            </div>
            <div className="absolute top-3 right-3 bg-white/80 p-1.5 rounded-full opacity-0 hover:opacity-100 transition-opacity">
              <ExternalLink className="w-4 h-4 text-gray-700" />
            </div>
          </div>

          <div 
            className="relative rounded-2xl overflow-hidden shadow-md cursor-pointer hover:shadow-xl transition-shadow"
            onClick={() => openLightbox(result.annotatedImageUrl, 'Annotated Image')}
          >
            <img 
              src={result.annotatedImageUrl} 
              alt="Annotated" 
              className="w-full h-48 md:h-56 object-cover"
            />
            <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors" />
            <div className="absolute bottom-3 left-3 bg-black/50 backdrop-blur-md text-white px-2 py-1 rounded-lg text-xs font-medium">
              Annotated
            </div>
            <div className="absolute top-3 right-3 bg-white/80 p-1.5 rounded-full opacity-0 hover:opacity-100 transition-opacity">
              <ExternalLink className="w-4 h-4 text-gray-700" />
            </div>
          </div>
        </div>
      </section>

      {/* Detection Summary */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold">
          Detection Summary
          {filterClass !== 'All Classes' && (
            <span className="ml-2 text-sm font-normal text-gray-500">
              (Filtered: {filterClass})
            </span>
          )}
        </h2>
        <div className="grid grid-cols-3 gap-3">
          <SummaryCard icon={<Users className="text-blue-500" />} value={filteredCounts.people} label="PEOPLE" />
          <SummaryCard icon={<Car className="text-blue-500" />} value={filteredCounts.vehicles} label="VEHICLES" />
          <SummaryCard icon={<BarChart3 className="text-blue-500" />} value={filteredCounts.total} label="TOTAL" />
        </div>
      </section>

      {/* Detection Data */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold">Detection Data</h2>
          <select 
            value={filterClass}
            onChange={(e) => setFilterClass(e.target.value)}
            className="bg-gray-50 border border-gray-200 rounded-lg px-2 py-1 text-sm outline-none cursor-pointer hover:bg-gray-100 transition-colors"
          >
            <option>All Classes</option>
            <option>Vehicles</option>
            <option>People</option>
          </select>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
          <table className="w-full text-left">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Class</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Conf.</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">BBox (x1, y1, x2, y2)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredDetections.length > 0 ? (
                filteredDetections.map((det) => (
                  <tr key={det.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-md text-xs font-bold ${
                        det.class === 'Vehicle' ? 'bg-blue-50 text-blue-600' : 'bg-red-50 text-red-600'
                      }`}>
                        {det.class}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-sm font-medium">{det.confidence.toFixed(2)}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{det.bbox.join(', ')}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="px-4 py-8 text-center text-gray-500">
                    No detections found for "{filterClass}"
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <button 
        onClick={() => downloadResults(result)}
        className="w-full py-4 bg-blue-600 text-white rounded-2xl font-semibold shadow-lg shadow-blue-200 hover:bg-blue-700 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
      >
        <Download className="w-5 h-5" />
        Download JSON Data
      </button>
    </div>
  );
}

function SummaryCard({ icon, value, label }: { icon: React.ReactNode, value: number, label: string }) {
  return (
    <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col items-center text-center">
      <div className="mb-2">{icon}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-[10px] font-bold text-gray-400 tracking-widest">{label}</div>
    </div>
  );
}

function HistoryView({ onSelect }: { onSelect: (res: DetectionResult) => void }) {
  return (
    <div className="p-6 sm:p-8 lg:p-12 space-y-4 max-w-7xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Past Detections</h2>
      {[1, 2, 3].map((i) => (
        <div 
          key={i} 
          onClick={() => onSelect(MOCK_RESULT)}
          className="flex items-center gap-4 p-4 bg-white border border-gray-100 rounded-2xl hover:border-blue-200 cursor-pointer transition-all hover:shadow-md"
        >
          <img 
            src={`https://picsum.photos/seed/hist${i}/200/200`} 
            className="w-16 h-16 rounded-xl object-cover" 
            referrerPolicy="no-referrer"
          />
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900">Detection #{1000 + i}</h4>
            <p className="text-xs text-gray-500">March {i + 1}, 2026 • 14:20</p>
            <div className="flex gap-2 mt-2">
              <span className="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded font-bold">48 VEHICLES</span>
              <span className="text-[10px] bg-red-50 text-red-600 px-1.5 py-0.5 rounded font-bold">12 PEOPLE</span>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-300" />
        </div>
      ))}
    </div>
  );
}

function SettingsView() {
  return (
    <div className="p-6 sm:p-8 lg:p-12 space-y-6 max-w-7xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Settings</h2>
      
      <div className="space-y-4">
        <div className="p-4 bg-white border border-gray-100 rounded-2xl space-y-4">
          <h3 className="font-semibold text-gray-900">Model Configuration</h3>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Auto-enhance images</span>
            <div className="w-10 h-5 bg-blue-600 rounded-full relative">
              <div className="absolute right-1 top-1 w-3 h-3 bg-white rounded-full" />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Save history locally</span>
            <div className="w-10 h-5 bg-gray-200 rounded-full relative">
              <div className="absolute left-1 top-1 w-3 h-3 bg-white rounded-full" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
