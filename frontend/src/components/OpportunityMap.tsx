import { useEffect, useRef, useState, useCallback, Component, ReactNode } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class MapErrorBoundary extends Component<{ children: ReactNode; fallback?: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode; fallback?: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="w-full h-[500px] bg-stone-800 rounded-lg flex items-center justify-center border border-stone-700">
          <div className="text-center p-6">
            <div className="text-4xl mb-4">🗺️</div>
            <p className="text-stone-300 mb-2">Map temporarily unavailable</p>
            <p className="text-sm text-stone-500">Geographic data is displayed in the sections below</p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

interface GeoJSONFeature {
  type: 'Feature';
  id?: string;
  geometry: GeoJSON.Geometry;
  properties: {
    layer: string;
    [key: string]: any;
  };
}

interface GeoJSONCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

interface MapMetadata {
  opportunity_id: number;
  category: string;
  center: { lat: number; lng: number };
  bounds: { radius_miles: number };
  signal_count: number;
  has_demographics: boolean;
}

interface LayerConfig {
  service_area: {
    type: string;
    visible: boolean;
    label: string;
    style?: {
      fillColor: string;
      fillOpacity: number;
      strokeColor: string;
      strokeWidth: number;
    };
  };
  opportunity_center: {
    type: string;
    visible: boolean;
    label: string;
  };
  heatmap: {
    type: string;
    visible: boolean;
    label: string;
    radius?: number;
    blur?: number;
  };
  growth_trajectory: {
    type: string;
    visible: boolean;
    label: string;
  };
}

interface MapDataResponse {
  geojson: GeoJSONCollection;
  metadata: MapMetadata;
  layer_config: LayerConfig;
}

interface LayerVisibility {
  service_area: boolean;
  heatmap: boolean;
  growth_trajectory: boolean;
  opportunity_center: boolean;
}

interface OpportunityMapProps {
  opportunityId: number;
  height?: string;
  showControls?: boolean;
  initialZoom?: number;
  className?: string;
}

const GROWTH_COLORS: Record<string, string> = {
  booming: '#22c55e',
  growing: '#84cc16',
  stable: '#facc15',
  declining: '#ef4444',
  unknown: '#6b7280'
};

const GROWTH_ICONS: Record<string, string> = {
  booming: '🚀',
  growing: '📈',
  stable: '➡️',
  declining: '📉',
  unknown: '❓'
};

export default function OpportunityMap({
  opportunityId,
  height = '500px',
  showControls = true,
  initialZoom = 10,
  className = ''
}: OpportunityMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapData, setMapData] = useState<MapDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    service_area: true,
    heatmap: true,
    growth_trajectory: true,
    opportunity_center: true
  });

  const fetchMapData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/v1/map/opportunity/${opportunityId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch map data: ${response.status}`);
      }
      const data: MapDataResponse = await response.json();
      setMapData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load map data');
    } finally {
      setLoading(false);
    }
  }, [opportunityId]);

  useEffect(() => {
    if (map.current) {
      map.current.remove();
      map.current = null;
    }
    fetchMapData();
  }, [fetchMapData]);

  useEffect(() => {
    if (!mapContainer.current || !mapData) return;
    
    if (map.current) {
      map.current.remove();
      map.current = null;
    }

    const accessToken = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN;
    if (!accessToken) {
      setError('Mapbox access token not configured');
      return;
    }

    mapboxgl.accessToken = accessToken;

    const { center } = mapData.metadata;
    
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [center.lng, center.lat],
      zoom: initialZoom,
      attributionControl: false
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.current.addControl(new mapboxgl.AttributionControl({ compact: true }), 'bottom-right');

    map.current.on('load', () => {
      if (!map.current || !mapData) return;

      const serviceAreaFeatures = mapData.geojson.features.filter(
        f => f.properties.layer === 'service_area'
      );
      if (serviceAreaFeatures.length > 0) {
        map.current.addSource('service-area', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: serviceAreaFeatures as any
          }
        });

        map.current.addLayer({
          id: 'service-area-fill',
          type: 'fill',
          source: 'service-area',
          paint: {
            'fill-color': mapData.layer_config.service_area.style?.fillColor || '#8B5CF6',
            'fill-opacity': mapData.layer_config.service_area.style?.fillOpacity || 0.15
          }
        });

        map.current.addLayer({
          id: 'service-area-outline',
          type: 'line',
          source: 'service-area',
          paint: {
            'line-color': mapData.layer_config.service_area.style?.strokeColor || '#8B5CF6',
            'line-width': mapData.layer_config.service_area.style?.strokeWidth || 2
          }
        });
      }

      const heatmapFeatures = mapData.geojson.features.filter(
        f => f.properties.layer === 'heatmap'
      );
      if (heatmapFeatures.length > 0) {
        map.current.addSource('heatmap', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: heatmapFeatures as any
          }
        });

        map.current.addLayer({
          id: 'heatmap-layer',
          type: 'heatmap',
          source: 'heatmap',
          paint: {
            'heatmap-weight': ['get', 'weight'],
            'heatmap-intensity': 1,
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0,0,0,0)',
              0.2, '#7c3aed',
              0.4, '#8b5cf6',
              0.6, '#a78bfa',
              0.8, '#c4b5fd',
              1, '#ede9fe'
            ],
            'heatmap-radius': mapData.layer_config.heatmap.radius || 25,
            'heatmap-opacity': 0.8
          }
        });
      }

      const growthFeatures = mapData.geojson.features.filter(
        f => f.properties.layer === 'growth_trajectory'
      );
      if (growthFeatures.length > 0) {
        map.current.addSource('growth-trajectory', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: growthFeatures as any
          }
        });

        map.current.addLayer({
          id: 'growth-trajectory-circles',
          type: 'circle',
          source: 'growth-trajectory',
          paint: {
            'circle-radius': 12,
            'circle-color': [
              'match',
              ['get', 'trajectory'],
              'booming', GROWTH_COLORS.booming,
              'growing', GROWTH_COLORS.growing,
              'stable', GROWTH_COLORS.stable,
              'declining', GROWTH_COLORS.declining,
              GROWTH_COLORS.unknown
            ],
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 0.9
          }
        });
      }

      const centerFeatures = mapData.geojson.features.filter(
        f => f.properties.layer === 'opportunity_center'
      );
      if (centerFeatures.length > 0) {
        map.current.addSource('opportunity-center', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: centerFeatures as any
          }
        });

        map.current.addLayer({
          id: 'opportunity-center-marker',
          type: 'circle',
          source: 'opportunity-center',
          paint: {
            'circle-radius': 10,
            'circle-color': '#8B5CF6',
            'circle-stroke-width': 3,
            'circle-stroke-color': '#ffffff'
          }
        });

        map.current.addLayer({
          id: 'opportunity-center-pulse',
          type: 'circle',
          source: 'opportunity-center',
          paint: {
            'circle-radius': 20,
            'circle-color': '#8B5CF6',
            'circle-opacity': 0.3,
            'circle-stroke-width': 0
          }
        });
      }

      map.current.on('click', 'growth-trajectory-circles', (e) => {
        if (!e.features || e.features.length === 0) return;
        const feature = e.features[0];
        const coordinates = (feature.geometry as any).coordinates.slice();
        const props = feature.properties;

        new mapboxgl.Popup()
          .setLngLat(coordinates)
          .setHTML(`
            <div class="text-sm p-2">
              <div class="font-semibold mb-1">${props?.county_name || 'Market Area'}</div>
              <div class="flex items-center gap-1 mb-1">
                <span>${GROWTH_ICONS[props?.trajectory] || '❓'}</span>
                <span class="capitalize">${props?.trajectory || 'Unknown'}</span>
              </div>
              ${props?.growth_rate !== undefined ? 
                `<div class="text-gray-400">Growth: ${(props.growth_rate * 100).toFixed(1)}%</div>` : ''}
              ${props?.signal_velocity !== undefined ? 
                `<div class="text-gray-400">Signal Velocity: ${props.signal_velocity.toFixed(2)}</div>` : ''}
            </div>
          `)
          .addTo(map.current!);
      });

      map.current.on('mouseenter', 'growth-trajectory-circles', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });

      map.current.on('mouseleave', 'growth-trajectory-circles', () => {
        if (map.current) map.current.getCanvas().style.cursor = '';
      });
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [mapData, initialZoom]);

  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    const layerMappings: Record<keyof LayerVisibility, string[]> = {
      service_area: ['service-area-fill', 'service-area-outline'],
      heatmap: ['heatmap-layer'],
      growth_trajectory: ['growth-trajectory-circles'],
      opportunity_center: ['opportunity-center-marker', 'opportunity-center-pulse']
    };

    Object.entries(layerVisibility).forEach(([key, visible]) => {
      const layers = layerMappings[key as keyof LayerVisibility];
      layers.forEach(layerId => {
        if (map.current?.getLayer(layerId)) {
          map.current.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
        }
      });
    });
  }, [layerVisibility]);

  const toggleLayer = (layer: keyof LayerVisibility) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  if (loading) {
    return (
      <div 
        className={`bg-stone-800 rounded-lg flex items-center justify-center border border-stone-700 ${className}`}
        style={{ height }}
      >
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full mx-auto mb-3"></div>
          <p className="text-stone-400">Loading map data...</p>
        </div>
      </div>
    );
  }

  if (error || !mapData) {
    return (
      <div 
        className={`bg-stone-800 rounded-lg flex items-center justify-center border border-stone-700 ${className}`}
        style={{ height }}
      >
        <div className="text-center p-6">
          <div className="text-4xl mb-4">🗺️</div>
          <p className="text-stone-300 mb-2">{error || 'Map data unavailable'}</p>
          <button
            onClick={fetchMapData}
            className="text-sm text-violet-400 hover:text-violet-300 underline"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <MapErrorBoundary>
      <div className={`relative ${className}`}>
        <div 
          ref={mapContainer} 
          style={{ height }} 
          className="rounded-lg overflow-hidden border border-stone-700"
        />
        
        {showControls && (
          <div className="absolute top-4 left-4 bg-stone-900/90 backdrop-blur-sm rounded-lg p-3 border border-stone-700">
            <div className="text-xs text-stone-400 uppercase tracking-wide mb-2">Layers</div>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.service_area}
                  onChange={() => toggleLayer('service_area')}
                  className="w-4 h-4 rounded border-stone-600 bg-stone-700 text-violet-500 focus:ring-violet-500"
                />
                <span className="text-sm text-stone-300">Service Area</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.heatmap}
                  onChange={() => toggleLayer('heatmap')}
                  className="w-4 h-4 rounded border-stone-600 bg-stone-700 text-violet-500 focus:ring-violet-500"
                />
                <span className="text-sm text-stone-300">Signal Heatmap</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.growth_trajectory}
                  onChange={() => toggleLayer('growth_trajectory')}
                  className="w-4 h-4 rounded border-stone-600 bg-stone-700 text-violet-500 focus:ring-violet-500"
                />
                <span className="text-sm text-stone-300">Growth Trajectory</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.opportunity_center}
                  onChange={() => toggleLayer('opportunity_center')}
                  className="w-4 h-4 rounded border-stone-600 bg-stone-700 text-violet-500 focus:ring-violet-500"
                />
                <span className="text-sm text-stone-300">Opportunity Center</span>
              </label>
            </div>
          </div>
        )}

        <div className="absolute bottom-4 left-4 bg-stone-900/90 backdrop-blur-sm rounded-lg p-2 border border-stone-700">
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-stone-400">Booming</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-lime-500"></div>
              <span className="text-stone-400">Growing</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <span className="text-stone-400">Stable</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-stone-400">Declining</span>
            </div>
          </div>
        </div>

        <div className="absolute top-4 right-16 bg-stone-900/90 backdrop-blur-sm rounded-lg px-3 py-2 border border-stone-700">
          <div className="text-xs text-stone-400">
            <span className="text-violet-400 font-medium">{mapData.metadata.signal_count}</span> signals detected
          </div>
        </div>
      </div>
    </MapErrorBoundary>
  );
}
