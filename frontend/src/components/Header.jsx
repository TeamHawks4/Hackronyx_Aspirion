import React from 'react';

export default function Header({ isOnline, activeLayer, activeYear, onToggleScenario, showScenario, onToggleStats, showStats }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo">🔥</div>
        <div>
          <h1 className="brand-title">Nagpur Urban Heat Island Intelligence</h1>
          <p className="brand-subtitle">Multi-Temporal Satellite Analytics & AI Prediction (2016–2025)</p>
        </div>
      </div>

      <div className="header-status">
        <div className="status-pill">
          <span className="status-dot"></span>
          <span>{isOnline ? 'API Connected' : 'Connecting…'}</span>
        </div>

        <button
          className={`btn btn-sm ${showScenario ? 'btn-warm' : 'btn-ghost'}`}
          onClick={onToggleScenario}
          title="What-if ML Scenario Simulator"
        >
          <span>🌱</span>
          <span>Scenario Simulator</span>
        </button>

        <button
          className={`btn btn-sm ${showStats ? 'btn-primary' : 'btn-ghost'}`}
          onClick={onToggleStats}
          title="Spatial Statistics & Trends"
        >
          <span>📊</span>
          <span>Analytics</span>
        </button>
      </div>
    </header>
  );
}
