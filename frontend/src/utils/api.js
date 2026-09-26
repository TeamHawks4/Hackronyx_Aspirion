import { API_BASE } from './constants';

async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export async function getMetadata() {
  return fetchJson(`${API_BASE}/metadata`);
}

export async function getPointValues(lat, lon) {
  return fetchJson(`${API_BASE}/analysis/point?lat=${lat}&lon=${lon}`);
}

export async function getTemporalTrend(lat, lon, layer = 'lst') {
  return fetchJson(`${API_BASE}/analysis/trend?lat=${lat}&lon=${lon}&layer=${layer}`);
}

export async function getZonalStats(bounds, year, layer = 'lst') {
  const { west, east, south, north } = bounds;
  return fetchJson(
    `${API_BASE}/analysis/zonal?west=${west}&east=${east}&south=${south}&north=${north}&year=${year}&layer=${layer}`
  );
}

export async function getCorrelation(year, xLayer = 'ndvi', yLayer = 'lst') {
  return fetchJson(`${API_BASE}/analysis/correlation?year=${year}&x_layer=${xLayer}&y_layer=${yLayer}`);
}

export async function runScenario(params) {
  return fetchJson(`${API_BASE}/scenario/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
}

export async function getModelInfo() {
  return fetchJson(`${API_BASE}/scenario/model-info`);
}

export function getLayerImageUrl(layer, year, opacity = 0.85) {
  if (layer === 'hotspots_persistent' || layer === 'water_mask') {
    return `${API_BASE}/layers/${layer}/image?opacity=${opacity}`;
  }
  return `${API_BASE}/layers/${layer}/${year}/image?opacity=${opacity}`;
}
