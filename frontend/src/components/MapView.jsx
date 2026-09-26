import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { NAGPUR_CENTER, DEFAULT_ZOOM } from '../utils/constants';
import { getLayerImageUrl } from '../utils/api';

const STUDY_BOUNDS = [
  [78.95, 21.26], // top-left [lon, lat]
  [79.20, 21.26], // top-right
  [79.20, 21.04], // bottom-right
  [78.95, 21.04], // bottom-left
];

const BASEMAP_TILES = {
  dark: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
  satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  streets: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
};

const BASEMAP_ATTRIBUTIONS = {
  dark: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
  satellite: '&copy; Esri &mdash; Earthstar Geographics',
  streets: '&copy; OpenStreetMap contributors',
};

export default function MapView({
  activeLayer,
  activeYear,
  opacity,
  basemap = 'dark',
  showBoundary = true,
  onMapClick,
  clickedCoord,
}) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {
          'base-tiles': {
            type: 'raster',
            tiles: [BASEMAP_TILES[basemap] || BASEMAP_TILES.dark],
            tileSize: 256,
            attribution: BASEMAP_ATTRIBUTIONS[basemap] || BASEMAP_ATTRIBUTIONS.dark,
          },
        },
        layers: [
          {
            id: 'base-tiles-layer',
            type: 'raster',
            source: 'base-tiles',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [NAGPUR_CENTER.lon, NAGPUR_CENTER.lat],
      zoom: DEFAULT_ZOOM,
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.addControl(new maplibregl.ScaleControl(), 'bottom-left');

    map.on('load', () => {
      // 1. Add UHI Raster Image source & layer
      const initialUrl = getLayerImageUrl(activeLayer, activeYear, 1.0);
      map.addSource('uhi-raster-source', {
        type: 'image',
        url: initialUrl,
        coordinates: STUDY_BOUNDS,
      });

      map.addLayer({
        id: 'uhi-raster-layer',
        type: 'raster',
        source: 'uhi-raster-source',
        paint: {
          'raster-opacity': opacity,
          'raster-resampling': 'linear',
        },
      });

      // 2. Add Reference labels (so city names appear legibly over raster)
      map.addSource('reference-labels-source', {
        type: 'raster',
        tiles: [
          'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
        ],
        tileSize: 256,
      });

      map.addLayer({
        id: 'reference-labels-layer',
        type: 'raster',
        source: 'reference-labels-source',
        minzoom: 0,
        maxzoom: 19,
        paint: {
          'raster-opacity': 0.85,
        },
      });

      // 3. Add Nagpur Municipal Boundary GeoJSON overlay
      map.addSource('nagpur-boundary-source', {
        type: 'geojson',
        data: '/api/metadata/boundary',
      });

      // Boundary line glow
      map.addLayer({
        id: 'nagpur-boundary-glow',
        type: 'line',
        source: 'nagpur-boundary-source',
        paint: {
          'line-color': '#0284c7',
          'line-width': 5,
          'line-opacity': 0.5,
          'line-blur': 3,
        },
      });

      // Boundary line stroke
      map.addLayer({
        id: 'nagpur-boundary-line',
        type: 'line',
        source: 'nagpur-boundary-source',
        paint: {
          'line-color': '#38bdf8',
          'line-width': 2,
          'line-dasharray': [3, 2],
        },
      });
    });

    map.on('click', (e) => {
      const { lng, lat } = e.lngLat;
      if (lng >= 78.95 && lng <= 79.20 && lat >= 21.04 && lat <= 21.26) {
        onMapClick({ lat, lon: lng });
      }
    });

    mapRef.current = map;

    return () => {
      map.remove();
    };
  }, []);

  // Update Basemap when basemap selection changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const source = map.getSource('base-tiles');
    if (source && source.setTiles) {
      source.setTiles([BASEMAP_TILES[basemap] || BASEMAP_TILES.dark]);
    }

    // Toggle reference labels depending on basemap
    if (map.getLayer('reference-labels-layer')) {
      map.setLayoutProperty(
        'reference-labels-layer',
        'visibility',
        basemap === 'dark' ? 'visible' : 'none'
      );
    }
  }, [basemap]);

  // Toggle boundary visibility
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const vis = showBoundary ? 'visible' : 'none';
    if (map.getLayer('nagpur-boundary-line')) {
      map.setLayoutProperty('nagpur-boundary-line', 'visibility', vis);
    }
    if (map.getLayer('nagpur-boundary-glow')) {
      map.setLayoutProperty('nagpur-boundary-glow', 'visibility', vis);
    }
  }, [showBoundary]);

  // Update raster image only when activeLayer or activeYear changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const newUrl = getLayerImageUrl(activeLayer, activeYear, 1.0);
    const source = map.getSource('uhi-raster-source');

    if (source) {
      try {
        source.updateImage({
          url: newUrl,
          coordinates: STUDY_BOUNDS,
        });
      } catch (err) {
        console.warn('Failed to update layer image:', err);
      }
    }
  }, [activeLayer, activeYear]);

  // Adjust layer opacity instantaneously via WebGL
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    if (map.getLayer('uhi-raster-layer')) {
      map.setPaintProperty('uhi-raster-layer', 'raster-opacity', opacity);
    }
  }, [opacity]);

  // Update marker on click
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (!clickedCoord) {
      if (markerRef.current) markerRef.current.remove();
      return;
    }

    if (!markerRef.current) {
      const el = document.createElement('div');
      el.className = 'map-click-marker';
      markerRef.current = new maplibregl.Marker({ element: el })
        .setLngLat([clickedCoord.lon, clickedCoord.lat])
        .addTo(map);
    } else {
      markerRef.current.setLngLat([clickedCoord.lon, clickedCoord.lat]);
    }
  }, [clickedCoord]);

  return (
    <div className="map-container" ref={mapContainerRef}></div>
  );
}
