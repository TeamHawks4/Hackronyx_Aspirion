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

export default function MapView({ activeLayer, activeYear, opacity, onMapClick, clickedCoord }) {
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
          osm: {
            type: 'raster',
            tiles: [
              'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
            ],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
          },
        },
        layers: [
          {
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [NAGPUR_CENTER.lon, NAGPUR_CENTER.lat],
      zoom: DEFAULT_ZOOM,
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-right');

    map.on('load', () => {
      // Add initial layer image source
      const initialUrl = getLayerImageUrl(activeLayer, activeYear, opacity);
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

  // Update raster layer when activeLayer, activeYear, or opacity changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const newUrl = getLayerImageUrl(activeLayer, activeYear, opacity);
    const source = map.getSource('uhi-raster-source');

    if (source) {
      source.updateImage({
        url: newUrl,
        coordinates: STUDY_BOUNDS,
      });
    }

    if (map.getLayer('uhi-raster-layer')) {
      map.setPaintProperty('uhi-raster-layer', 'raster-opacity', opacity);
    }
  }, [activeLayer, activeYear, opacity]);

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
