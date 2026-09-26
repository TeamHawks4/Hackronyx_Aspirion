import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';

export default function StatsPanel({ pointData, clickedCoord, activeYear, onClose }) {
  const trendData = pointData?.values?.map((v) => ({
    year: v.year,
    lst: v.lst,
    ndvi: v.ndvi ? Math.round(v.ndvi * 100) / 100 : null,
    ndbi: v.ndbi ? Math.round(v.ndbi * 100) / 100 : null,
  })) || [];

  const currentYearValues = pointData?.values?.find((v) => v.year === activeYear) || pointData?.values?.[pointData.values.length - 1];

  return (
    <div className="glass-card panel-card animate-slide">
      <div className="section-header" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="section-icon" style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#22c55e' }}>
            📈
          </div>
          <div className="section-title">Point Inspection & Trends</div>
        </div>
        {onClose && (
          <button className="btn btn-ghost btn-sm" onClick={onClose} style={{ padding: '2px 8px' }}>
            ✕
          </button>
        )}
      </div>

      {clickedCoord ? (
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Lat: {clickedCoord.lat.toFixed(4)}°, Lon: {clickedCoord.lon.toFixed(4)}°
        </div>
      ) : (
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          Click anywhere on the map of Nagpur to inspect temporal surface indices and heat metrics.
        </div>
      )}

      {currentYearValues && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <div className="stat-card">
            <div className="stat-label">LST ({activeYear})</div>
            <div className="stat-value" style={{ color: 'var(--accent-red)' }}>
              {currentYearValues.lst ? `${currentYearValues.lst.toFixed(1)}°C` : 'N/A'}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">NDVI (Vegetation)</div>
            <div className="stat-value" style={{ color: 'var(--accent-green)' }}>
              {currentYearValues.ndvi !== undefined ? currentYearValues.ndvi.toFixed(2) : 'N/A'}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">NDBI (Built-up)</div>
            <div className="stat-value" style={{ color: 'var(--accent-orange)' }}>
              {currentYearValues.ndbi !== undefined ? currentYearValues.ndbi.toFixed(2) : 'N/A'}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Hotspot Score</div>
            <div className="stat-value" style={{ color: 'var(--accent-cyan)' }}>
              {pointData?.hotspot_score !== null && pointData?.hotspot_score !== undefined
                ? pointData.hotspot_score.toFixed(2)
                : '0.00'}
            </div>
          </div>
        </div>
      )}

      {/* Multi-temporal Trend Line Chart */}
      {trendData.length > 0 && (
        <div>
          <div className="section-title" style={{ fontSize: '11px', margin: '8px 0 6px 0' }}>
            Multi-Temporal LST Trend (2016–2025)
          </div>
          <div style={{ width: '100%', height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
                <YAxis domain={['auto', 'auto']} stroke="#64748b" fontSize={11} unit="°C" />
                <Tooltip
                  contentStyle={{
                    background: '#0f172a',
                    borderColor: 'rgba(56, 189, 248, 0.3)',
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="lst"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#ef4444' }}
                  name="LST (°C)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
