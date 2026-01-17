import { useEffect, useRef, useState, useCallback, Component, ReactNode } from 'react';
import Map, { Marker, Popup, Source, Layer, NavigationControl, ViewStateChangeEvent } from 'react-map-gl';
import type { MapRef } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || '';

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
        <div className="w-full h-[500px] bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center p-6">
            <div className="text-4xl mb-4">🗺️</div>
            <p className="text-gray-600 mb-2">Map temporarily unavailable</p>
            <p className="text-sm text-gray-500">The results are displayed below</p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

interface Pin {
  id: number;
  lat: number;
  lng: number;
  name: string;
  rating?: number;
  reviews?: number;
  source: string;
  popup?: string;
}

interface HeatmapPoint {
  lat: number;
  lng: number;
  intensity: number;
  title?: string;
  source: string;
}

interface MapData {
  bounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  center?: {
    lat: number;
    lng: number;
  };
  layers: {
    pins: { data: Pin[]; count: number };
    heatmap: { data: HeatmapPoint[]; count: number };
    polygons: { data: any[]; count: number };
  };
  totalFeatures: number;
}

interface LayerState {
  pins: boolean;
  heatmap: boolean;
  polygons: boolean;
}

interface ConsultantMapProps {
  mapData: MapData | null;
  city?: string;
  isLoading?: boolean;
}

export default function ConsultantMap({ mapData, city, isLoading }: ConsultantMapProps) {
  const mapRef = useRef<MapRef>(null);
  const [selectedPin, setSelectedPin] = useState<Pin | null>(null);
  const [layerState, setLayerState] = useState<LayerState>({
    pins: true,
    heatmap: true,
    polygons: true,
  });
  
  const [viewState, setViewState] = useState({
    longitude: -98.5795,
    latitude: 39.8283,
    zoom: 4,
  });
  
  useEffect(() => {
    if (mapData?.center) {
      setViewState({
        longitude: mapData.center.lng,
        latitude: mapData.center.lat,
        zoom: 11,
      });
    }
  }, [mapData?.center]);
  
  const toggleLayer = useCallback((layer: keyof LayerState) => {
    setLayerState(prev => ({ ...prev, [layer]: !prev[layer] }));
  }, []);
  
  const heatmapGeoJSON = {
    type: 'FeatureCollection' as const,
    features: (mapData?.layers?.heatmap?.data || []).map((point) => ({
      type: 'Feature' as const,
      properties: {
        intensity: point.intensity,
        title: point.title,
      },
      geometry: {
        type: 'Point' as const,
        coordinates: [point.lng, point.lat],
      },
    })),
  };
  
  const polygonGeoJSON = {
    type: 'FeatureCollection' as const,
    features: (mapData?.layers?.polygons?.data || []).filter(g => g?.geometry?.type === 'Polygon'),
  };
  
  if (isLoading) {
    return (
      <div className="w-full h-[500px] bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading map data for {city}...</p>
        </div>
      </div>
    );
  }
  
  if (!MAPBOX_TOKEN) {
    return (
      <div className="w-full h-[500px] bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center p-6">
          <div className="text-4xl mb-4">🗺️</div>
          <p className="text-gray-600 mb-2">Map configuration pending</p>
          <p className="text-sm text-gray-500">Mapbox access token not configured</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3 px-2">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => toggleLayer('pins')}
            className={`px-3 py-1.5 text-sm rounded-full flex items-center gap-1.5 transition-colors ${
              layerState.pins 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-blue-400"></span>
            Business Pins ({mapData?.layers?.pins?.count || 0})
          </button>
          <button
            onClick={() => toggleLayer('heatmap')}
            className={`px-3 py-1.5 text-sm rounded-full flex items-center gap-1.5 transition-colors ${
              layerState.heatmap 
                ? 'bg-orange-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-orange-400"></span>
            Problem Heatmap ({mapData?.layers?.heatmap?.count || 0})
          </button>
          <button
            onClick={() => toggleLayer('polygons')}
            className={`px-3 py-1.5 text-sm rounded-full flex items-center gap-1.5 transition-colors ${
              layerState.polygons 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-purple-400"></span>
            Neighborhoods ({mapData?.layers?.polygons?.count || 0})
          </button>
        </div>
        <div className="text-sm text-gray-500">
          {mapData?.totalFeatures || 0} total features
        </div>
      </div>
      
      <MapErrorBoundary>
        <div className="rounded-lg overflow-hidden border border-gray-200 shadow-sm">
          <Map
            ref={mapRef}
            {...viewState}
            onMove={(evt: ViewStateChangeEvent) => setViewState(evt.viewState)}
            style={{ width: '100%', height: 500 }}
            mapStyle="mapbox://styles/mapbox/light-v11"
            mapboxAccessToken={MAPBOX_TOKEN}
          >
            <NavigationControl position="top-right" />
            
            {layerState.polygons && polygonGeoJSON.features.length > 0 && (
              <Source id="polygons" type="geojson" data={polygonGeoJSON}>
                <Layer
                  id="polygon-fill"
                  type="fill"
                  paint={{
                    'fill-color': '#9C27B0',
                    'fill-opacity': 0.2,
                  }}
                />
                <Layer
                  id="polygon-outline"
                  type="line"
                  paint={{
                    'line-color': '#7B1FA2',
                    'line-width': 2,
                  }}
                />
              </Source>
            )}
            
            {layerState.heatmap && heatmapGeoJSON.features.length > 0 && (
              <Source id="heatmap" type="geojson" data={heatmapGeoJSON}>
                <Layer
                  id="heatmap-layer"
                  type="heatmap"
                  paint={{
                    'heatmap-weight': ['get', 'intensity'],
                    'heatmap-intensity': 1,
                    'heatmap-color': [
                      'interpolate',
                      ['linear'],
                      ['heatmap-density'],
                      0, 'rgba(0,0,255,0)',
                      0.2, 'royalblue',
                      0.4, 'cyan',
                      0.6, 'lime',
                      0.8, 'yellow',
                      1, 'red'
                    ],
                    'heatmap-radius': 30,
                    'heatmap-opacity': 0.7,
                  }}
                />
              </Source>
            )}
            
            {layerState.pins && mapData?.layers?.pins?.data?.map((pin) => (
              <Marker
                key={`pin-${pin.id}`}
                longitude={pin.lng}
                latitude={pin.lat}
                anchor="bottom"
                onClick={(e: { originalEvent: MouseEvent }) => {
                  e.originalEvent.stopPropagation();
                  setSelectedPin(pin);
                }}
              >
                <div 
                  className={`w-6 h-6 rounded-full border-2 border-white shadow-lg cursor-pointer transform hover:scale-110 transition-transform ${
                    pin.source === 'yelp' ? 'bg-red-500' : 'bg-blue-500'
                  }`}
                />
              </Marker>
            ))}
            
            {selectedPin && (
              <Popup
                longitude={selectedPin.lng}
                latitude={selectedPin.lat}
                anchor="bottom"
                onClose={() => setSelectedPin(null)}
                closeButton={true}
                closeOnClick={false}
              >
                <div className="min-w-[200px] p-2">
                  <h3 className="font-semibold text-gray-900">{selectedPin.name}</h3>
                  {selectedPin.rating && (
                    <div className="flex items-center gap-1 mt-1">
                      <span className="text-yellow-500">★</span>
                      <span>{selectedPin.rating}</span>
                      {selectedPin.reviews && <span className="text-gray-500">({selectedPin.reviews} reviews)</span>}
                    </div>
                  )}
                  <div className="mt-2 text-xs text-gray-500 capitalize">
                    Source: {selectedPin.source?.replace('_', ' ')}
                  </div>
                </div>
              </Popup>
            )}
          </Map>
        </div>
      </MapErrorBoundary>
      
      {!mapData?.totalFeatures && !isLoading && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 text-sm">
            No geographic data available for this location yet. Data is populated through our webhook ingestion pipeline.
          </p>
        </div>
      )}
    </div>
  );
}
