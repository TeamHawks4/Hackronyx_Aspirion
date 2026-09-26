import React from 'react';
import { LAYERS, LULC_CLASSES } from '../utils/constants';

export default function LayerControl({
  activeLayer,
  onSelectLayer,
  opacity,
  onChangeOpacity,
  basemap,
  onChangeBasemap,
  showBoundary,
  onToggleBoundary,
}) {
  return (
    <div className="glass-card panel-card animate-in">
      {/* ── Geospatial Layers Section ──────────────────────────────── */}
      <div className="section-header">
        <div className="section-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
          🗺️
        </div>
        <div className="section-title">Surface Heat & Index Layers</div>
      </div>

      <div className="layer-grid">
        {Object.entries(LAYERS).map(([key, config]) => (
          <button
            key={key}
            className={`layer-pill ${activeLayer === key ? 'active' : ''}`}
            onClick={() => onSelectLayer(key)}
          >
            <span style={{ fontSize: '15px' }}>{config.icon}</span>
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{config.label}</span>
          </button>
        ))}
      </div>

      <div className="divider"></div>

      {/* ── Basemap Selector ────────────────────────────────────────── */}
      <div className="section-header" style={{ marginBottom: '8px' }}>
        <div className="section-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', width: 22, height: 22, fontSize: '11px' }}>
          🌐
        </div>
        <div className="section-title" style={{ fontSize: '11px' }}>Basemap Style</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
        {[
          { id: 'dark', label: 'Dark Canvas', icon: '🌙' },
          { id: 'satellite', label: 'Satellite', icon: '🛰️' },
          { id: 'streets', label: 'Street Map', icon: '🗺️' },
        ].map((item) => (
          <button
            key={item.id}
            className={`btn btn-ghost btn-sm ${basemap === item.id ? 'active' : ''}`}
            style={{
              padding: '6px 8px',
              fontSize: '11px',
              justifyContent: 'center',
              background: basemap === item.id ? 'rgba(56, 189, 248, 0.18)' : 'var(--bg-input)',
              borderColor: basemap === item.id ? 'var(--accent-cyan)' : 'var(--border-subtle)',
              color: basemap === item.id ? '#ffffff' : 'var(--text-secondary)',
            }}
            onClick={() => onChangeBasemap(item.id)}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>

      {/* Boundary Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '10px', padding: '6px 10px', background: 'var(--bg-input)', borderRadius: 'var(--radius-md)' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#38bdf8' }}></span>
          Nagpur City Boundary
        </span>
        <input
          type="checkbox"
          checked={showBoundary}
          onChange={(e) => onToggleBoundary(e.target.checked)}
          style={{ cursor: 'pointer', accentColor: '#38bdf8' }}
        />
      </div>

      <div className="divider"></div>

      {/* ── Layer Opacity ───────────────────────────────────────────── */}
      <div className="slider-container">
        <div className="slider-label">
          <span>Layer Opacity</span>
          <span className="slider-value">{Math.round(opacity * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.1"
          max="1.0"
          step="0.05"
          value={opacity}
          onChange={(e) => onChangeOpacity(parseFloat(e.target.value))}
        />
      </div>

      <div className="divider"></div>

      {/* ── Dynamic Legend ──────────────────────────────────────────── */}
      <div className="legend-container">
        <div className="section-title" style={{ fontSize: '11px' }}>Color Ramp Legend</div>

        {activeLayer === 'lst' && (
          <div>
            <div className="heat-gradient-bar"></div>
            <div className="gradient-labels">
              <span>25°C (Cool/Water)</span>
              <span>40°C</span>
              <span>55°C (Extreme Heat)</span>
            </div>
          </div>
        )}

        {activeLayer === 'ndvi' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, #8b5a2b, #fef08a, #22c55e, #14532d)' }}></div>
            <div className="gradient-labels">
              <span>-0.2 (Barren/Pavement)</span>
              <span>0.3 (Canopy)</span>
              <span>0.85 (Dense Flora)</span>
            </div>
          </div>
        )}

        {activeLayer === 'ndbi' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, #22c55e, #94a3b8, #fb923c, #ef4444)' }}></div>
            <div className="gradient-labels">
              <span>-0.4 (Pervious/Veg)</span>
              <span>0.1 (Suburban)</span>
              <span>0.6 (Commercial Core)</span>
            </div>
          </div>
        )}

        {activeLayer === 'ndwi' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, #d4a574, #38bdf8, #1d4ed8)' }}></div>
            <div className="gradient-labels">
              <span>-0.5 (Dry Soil)</span>
              <span>0.1</span>
              <span>0.7 (Water Body)</span>
            </div>
          </div>
        )}

        {activeLayer === 'lulc' && (
          <div className="legend-categorical">
            {Object.entries(LULC_CLASSES).map(([idx, item]) => (
              <div key={idx} className="legend-cat-item">
                <span className="cat-color-dot" style={{ background: item.color }}></span>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        )}

        {activeLayer === 'hotspots_persistent' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, transparent, #fbbf24, #f97316, #dc2626)' }}></div>
            <div className="gradient-labels">
              <span>Low</span>
              <span>Moderate</span>
              <span>Critical UHI Core</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
