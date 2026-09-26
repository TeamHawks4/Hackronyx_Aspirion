import React from 'react';
import { LAYERS, LULC_CLASSES } from '../utils/constants';

export default function LayerControl({
  activeLayer,
  onSelectLayer,
  opacity,
  onChangeOpacity,
}) {
  return (
    <div className="glass-card panel-card animate-in">
      <div className="section-header">
        <div className="section-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
          🗺️
        </div>
        <div className="section-title">Geospatial Layers</div>
      </div>

      <div className="layer-grid">
        {Object.entries(LAYERS).map(([key, config]) => (
          <button
            key={key}
            className={`layer-pill ${activeLayer === key ? 'active' : ''}`}
            onClick={() => onSelectLayer(key)}
          >
            <span>{config.icon}</span>
            <span>{config.label}</span>
          </button>
        ))}
      </div>

      <div className="divider"></div>

      {/* Layer Opacity */}
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

      {/* Dynamic Legend */}
      <div className="legend-container">
        <div className="section-title" style={{ fontSize: '11px' }}>Legend</div>

        {activeLayer === 'lst' && (
          <div>
            <div className="heat-gradient-bar"></div>
            <div className="gradient-labels">
              <span>25°C (Cool)</span>
              <span>40°C</span>
              <span>55°C (Extreme)</span>
            </div>
          </div>
        )}

        {activeLayer === 'ndvi' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, #8b5a2b, #fef08a, #22c55e, #14532d)' }}></div>
            <div className="gradient-labels">
              <span>-0.2 (Barren/Water)</span>
              <span>0.3</span>
              <span>0.85 (Dense Green)</span>
            </div>
          </div>
        )}

        {activeLayer === 'ndbi' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, #22c55e, #94a3b8, #fb923c, #ef4444)' }}></div>
            <div className="gradient-labels">
              <span>-0.4 (Veg)</span>
              <span>0.1 (Suburban)</span>
              <span>0.6 (High Built)</span>
            </div>
          </div>
        )}

        {activeLayer === 'ndwi' && (
          <div>
            <div className="heat-gradient-bar" style={{ background: 'linear-gradient(90deg, #d4a574, #38bdf8, #1d4ed8)' }}></div>
            <div className="gradient-labels">
              <span>-0.5 (Dry)</span>
              <span>0.1</span>
              <span>0.7 (Water)</span>
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
