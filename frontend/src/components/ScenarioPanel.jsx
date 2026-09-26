import React, { useState } from 'react';
import { runScenario } from '../utils/api';

export default function ScenarioPanel({ bounds, activeYear, onClose }) {
  const [ndviChange, setNdviChange] = useState(0.20);
  const [ndbiChange, setNdbiChange] = useState(-0.15);
  const [ndwiChange, setNdwiChange] = useState(0.05);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runScenario({
        west: bounds?.west || 79.05,
        east: bounds?.east || 79.15,
        south: bounds?.south || 21.10,
        north: bounds?.north || 21.20,
        year: activeYear,
        ndvi_change: ndviChange,
        ndbi_change: ndbiChange,
        ndwi_change: ndwiChange,
      });
      setResult(res);
    } catch (err) {
      setError(err.message || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card panel-card animate-slide">
      <div className="section-header" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="section-icon" style={{ background: 'rgba(251, 146, 60, 0.15)', color: '#fb923c' }}>
            🌱
          </div>
          <div className="section-title">Scenario Simulator (AI)</div>
        </div>
        {onClose && (
          <button className="btn btn-ghost btn-sm" onClick={onClose} style={{ padding: '2px 8px' }}>
            ✕
          </button>
        )}
      </div>

      <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
        Simulate urban greening, cool pavements, or water retention to estimate Land Surface Temperature mitigation.
      </p>

      {/* Sliders */}
      <div className="slider-container">
        <div className="slider-label">
          <span>🌿 Vegetation Cover (NDVI)</span>
          <span className="slider-value">{ndviChange >= 0 ? `+${ndviChange.toFixed(2)}` : ndviChange.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min="-0.5"
          max="0.5"
          step="0.05"
          value={ndviChange}
          onChange={(e) => setNdviChange(parseFloat(e.target.value))}
        />
      </div>

      <div className="slider-container">
        <div className="slider-label">
          <span>🏗️ Built Surface Density (NDBI)</span>
          <span className="slider-value">{ndbiChange >= 0 ? `+${ndbiChange.toFixed(2)}` : ndbiChange.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min="-0.5"
          max="0.5"
          step="0.05"
          value={ndbiChange}
          onChange={(e) => setNdbiChange(parseFloat(e.target.value))}
        />
      </div>

      <div className="slider-container">
        <div className="slider-label">
          <span>💧 Water Bodies & Moisture (NDWI)</span>
          <span className="slider-value">{ndwiChange >= 0 ? `+${ndwiChange.toFixed(2)}` : ndwiChange.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min="-0.3"
          max="0.3"
          step="0.05"
          value={ndwiChange}
          onChange={(e) => setNdwiChange(parseFloat(e.target.value))}
        />
      </div>

      <button className="btn btn-warm" onClick={handleSimulate} disabled={loading} style={{ justifyContent: 'center' }}>
        <span>{loading ? '⚡ Running ML Model…' : '🔮 Run Intervention Scenario'}</span>
      </button>

      {error && (
        <div style={{ color: '#ef4444', fontSize: '12px' }}>{error}</div>
      )}

      {/* Results */}
      {result && (
        <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div className="divider" style={{ margin: '8px 0' }}></div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div className="stat-card">
              <div className="stat-label">Baseline LST</div>
              <div className="stat-value">{result.base_lst_mean}°C</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Scenario LST</div>
              <div className="stat-value" style={{ color: result.delta_lst <= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                {result.scenario_lst_mean}°C
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-input)', borderRadius: 'var(--radius-md)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Estimated Temperature Delta</span>
            <span
              className={`badge ${result.delta_lst <= 0 ? 'badge-cool' : 'badge-hot'}`}
              style={{ fontSize: '13px', padding: '4px 10px' }}
            >
              {result.delta_lst > 0 ? `+${result.delta_lst}°C` : `${result.delta_lst}°C`}
            </span>
          </div>

          {/* SHAP Feature attribution */}
          {result.shap_features && (
            <div>
              <div className="section-title" style={{ fontSize: '11px', marginBottom: '6px' }}>
                SHAP Feature Attribution
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {result.shap_features.slice(0, 4).map((f) => (
                  <div key={f.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-secondary)', textTransform: 'uppercase' }}>{f.name}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: f.shap_value <= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                      {f.shap_value > 0 ? `+${f.shap_value.toFixed(2)}°C` : `${f.shap_value.toFixed(2)}°C`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="disclaimer-banner">
            ⚠️ {result.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
}
