import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MapView from './components/MapView';
import LayerControl from './components/LayerControl';
import TimeSlider from './components/TimeSlider';
import ScenarioPanel from './components/ScenarioPanel';
import StatsPanel from './components/StatsPanel';
import { getMetadata, getPointValues } from './utils/api';
import './App.css';

export default function App() {
  const [isOnline, setIsOnline] = useState(false);
  const [metadata, setMetadata] = useState(null);
  const [activeLayer, setActiveLayer] = useState('lst');
  const [activeYear, setActiveYear] = useState(2025);
  const [opacity, setOpacity] = useState(0.85);

  const [clickedCoord, setClickedCoord] = useState(null);
  const [pointData, setPointData] = useState(null);

  const [showScenario, setShowScenario] = useState(false);
  const [showStats, setShowStats] = useState(true);

  // Fetch metadata on mount
  useEffect(() => {
    getMetadata()
      .then((data) => {
        setMetadata(data);
        setIsOnline(true);
      })
      .catch((err) => {
        console.warn('Metadata fetch failed:', err);
        setIsOnline(false);
      });
  }, []);

  // Handle map click
  const handleMapClick = async ({ lat, lon }) => {
    setClickedCoord({ lat, lon });
    setShowStats(true);
    try {
      const data = await getPointValues(lat, lon);
      setPointData(data);
    } catch (err) {
      console.error('Failed to get point data:', err);
    }
  };

  return (
    <div className="app-container">
      <Header
        isOnline={isOnline}
        activeLayer={activeLayer}
        activeYear={activeYear}
        showScenario={showScenario}
        onToggleScenario={() => setShowScenario(!showScenario)}
        showStats={showStats}
        onToggleStats={() => setShowStats(!showStats)}
      />

      <main className="main-view">
        <MapView
          activeLayer={activeLayer}
          activeYear={activeYear}
          opacity={opacity}
          onMapClick={handleMapClick}
          clickedCoord={clickedCoord}
        />

        {/* Floating Left: Layer Selection & Legend */}
        <aside className="floating-sidebar-left">
          <LayerControl
            activeLayer={activeLayer}
            onSelectLayer={setActiveLayer}
            opacity={opacity}
            onChangeOpacity={setOpacity}
          />
        </aside>

        {/* Floating Right: Stats & Scenario Panels */}
        <aside className="floating-sidebar-right">
          {showScenario && (
            <ScenarioPanel
              bounds={metadata?.bounds}
              activeYear={activeYear}
              onClose={() => setShowScenario(false)}
            />
          )}

          {showStats && (
            <StatsPanel
              pointData={pointData}
              clickedCoord={clickedCoord}
              activeYear={activeYear}
              onClose={() => setShowStats(false)}
            />
          )}
        </aside>

        {/* Bottom Time Progression Slider */}
        <TimeSlider
          activeYear={activeYear}
          onSelectYear={setActiveYear}
        />
      </main>
    </div>
  );
}
