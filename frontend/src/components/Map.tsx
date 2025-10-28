'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getMapColor } from '@/lib/utils';
import type { GeoJSONFeatureCollection } from '@/lib/types';

interface MapProps {
  data: GeoJSONFeatureCollection | null;
  onFeatureClick?: (projectId: number) => void;
  center?: [number, number];
  zoom?: number;
}

export default function Map({ data, onFeatureClick, center = [20.5937, 78.9629], zoom = 5 }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.GeoJSON | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    // Initialize map
    const map = L.map(mapContainer.current).setView(center, zoom);

    // Add tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !data) return;

    // Remove existing layer
    if (layerRef.current) {
      mapRef.current.removeLayer(layerRef.current);
    }

    // Add GeoJSON layer
    const layer = L.geoJSON(data as any, {
      style: (feature) => {
        const status = feature?.properties?.status;
        return {
          color: getMapColor(status),
          weight: 4,
          opacity: 0.8,
        };
      },
      onEachFeature: (feature, layer) => {
        const props = feature.properties;
        
        // Bind popup
        layer.bindPopup(`
          <div class="p-2">
            <h3 class="font-bold text-sm mb-1">${props.project_name}</h3>
            <p class="text-xs text-gray-600">${props.district}, ${props.city || ''}</p>
            <p class="text-xs mt-1">
              <span class="font-medium">Status:</span> ${props.status}
            </p>
            <p class="text-xs">
              <span class="font-medium">Contractor:</span> ${props.contractor || 'N/A'}
            </p>
            <button
              onclick="window.location.href='/projects/${props.project_id}'"
              class="mt-2 text-xs bg-primary-600 text-white px-3 py-1 rounded hover:bg-primary-700"
            >
              View Details
            </button>
          </div>
        `);

        // Click handler
        layer.on('click', () => {
          if (onFeatureClick) {
            onFeatureClick(props.project_id);
          }
        });
      },
    });

    layer.addTo(mapRef.current);
    layerRef.current = layer;

    // Fit bounds to show all features
    if (data.features.length > 0) {
      const bounds = layer.getBounds();
      mapRef.current.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [data, onFeatureClick]);

  return (
    <div ref={mapContainer} className="w-full h-full min-h-[500px] rounded-lg overflow-hidden shadow-lg" />
  );
}