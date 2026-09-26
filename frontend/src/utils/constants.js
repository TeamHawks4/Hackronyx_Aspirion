export const API_BASE = '/api';

export const NAGPUR_CENTER = { lat: 21.1458, lon: 79.0882 };

export const DEFAULT_ZOOM = 11.5;

export const YEARS = [2016, 2019, 2022, 2025];

export const LAYERS = {
  lst:  { label: 'Land Surface Temperature', unit: '°C', icon: '🌡️', color: '#ef4444' },
  ndvi: { label: 'Vegetation Index (NDVI)', unit: '', icon: '🌿', color: '#22c55e' },
  ndbi: { label: 'Built-up Index (NDBI)', unit: '', icon: '🏗️', color: '#fb923c' },
  ndwi: { label: 'Water Index (NDWI)', unit: '', icon: '💧', color: '#3b82f6' },
  lulc: { label: 'Land Use / Land Cover', unit: '', icon: '🗺️', color: '#6366f1' },
  hotspots_persistent: { label: 'Persistent Hotspots', unit: '', icon: '🔥', color: '#ef4444' },
};

export const LULC_CLASSES = {
  0: { label: 'Water', color: '#2563eb' },
  1: { label: 'Dense Vegetation', color: '#16a34a' },
  2: { label: 'Sparse Vegetation', color: '#84cc16' },
  3: { label: 'Built-up (Low)', color: '#f59e0b' },
  4: { label: 'Built-up (High)', color: '#dc2626' },
  5: { label: 'Barren / Open', color: '#d4a574' },
};
