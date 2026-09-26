import React, { useState, useEffect } from 'react';
import { YEARS } from '../utils/constants';

export default function TimeSlider({ activeYear, onSelectYear }) {
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      onSelectYear((prevYear) => {
        const idx = YEARS.indexOf(prevYear);
        const nextIdx = (idx + 1) % YEARS.length;
        return YEARS[nextIdx];
      });
    }, 2000);
    return () => clearInterval(interval);
  }, [isPlaying, onSelectYear]);

  return (
    <div className="bottom-controls">
      <div className="glass-card timeline-bar animate-in">
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setIsPlaying(!isPlaying)}
          title={isPlaying ? 'Pause auto-play' : 'Play multi-temporal progression'}
        >
          <span>{isPlaying ? '⏸️' : '▶️'}</span>
          <span>{isPlaying ? 'Pause' : 'Play'}</span>
        </button>

        <div className="year-buttons">
          {YEARS.map((year) => (
            <button
              key={year}
              className={`year-btn ${activeYear === year ? 'active' : ''}`}
              onClick={() => {
                setIsPlaying(false);
                onSelectYear(year);
              }}
            >
              {year}
            </button>
          ))}
        </div>

        <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Nagpur Study Area
        </div>
      </div>
    </div>
  );
}
