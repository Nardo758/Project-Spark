import { useEffect, useRef, useState, useCallback, useMemo, Component, ReactNode } from 'react';
import Map, { Marker, Popup, Source, Layer, NavigationControl, ViewStateChangeEvent } from 'react-map-gl';
import type { MapRef } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || '';

if (!MAPBOX_TOKEN && import.meta.env.PROD) {
  console.warn('[ConsultantMap] MAPBOX_ACCESS_TOKEN not configured for production build');
}

const COMPETITOR_RADIUS_MILES = 0.5;
const GRID_SIZE = 10;

function createCirclePolygon(lat: number, lng: number, radiusMiles: number, points: number = 32): [number, number][] {
  const radiusKm = radiusMiles * 1.60934;
  const coords: [number, number][] = [];
  for (let i = 0; i <= points; i++) {
    const angle = (i / points) * 2 * Math.PI;
    const latOffset = (radiusKm / 111) * Math.cos(angle);
    const lngOffset = (radiusKm / (111 * Math.cos(lat * Math.PI / 180))) * Math.sin(angle);
    coords.push([lng + lngOffset, lat + latOffset]);
  }
  return coords;
}

function calculateDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 3959;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

interface GridCell {
  lat: number;
  lng: number;
  score: number;
  minDistance: number;
  inCompetitorZone: boolean;
}

const GRID_RADIUS_MILES = 1.5;
const MAX_SCORE_DISTANCE = 1.5;

function generateOpportunityGrid(
  pins: Pin[],
  center: { lat: number; lng: number },
  gridSize: number = GRID_SIZE
): GridCell[] {
  const cells: GridCell[] = [];
  const radiusMiles = GRID_RADIUS_MILES;
  const stepLat = (radiusMiles * 2 / 111) / gridSize;
  const stepLng = (radiusMiles * 2 / (111 * Math.cos(center.lat * Math.PI / 180))) / gridSize;
  
  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      const cellLat = center.lat - (radiusMiles / 111) + (i + 0.5) * stepLat;
      const cellLng = center.lng - (radiusMiles / (111 * Math.cos(center.lat * Math.PI / 180))) + (j + 0.5) * stepLng;
      
      let minDistance = Infinity;
      for (const pin of pins) {
        const dist = calculateDistance(cellLat, cellLng, pin.lat, pin.lng);
        if (dist < minDistance) minDistance = dist;
      }
      
      const inCompetitorZone = minDistance < COMPETITOR_RADIUS_MILES;
      let score: number;
      if (inCompetitorZone) {
        score = 0;
      } else {
        const maxExtraDistance = MAX_SCORE_DISTANCE - COMPETITOR_RADIUS_MILES;
        if (maxExtraDistance <= 0) {
          score = 100;
        } else {
          const distanceBeyondZone = minDistance - COMPETITOR_RADIUS_MILES;
          score = Math.min(100, Math.max(0, (distanceBeyondZone / maxExtraDistance) * 100));
        }
      }
      
      cells.push({ lat: cellLat, lng: cellLng, score, minDistance, inCompetitorZone });
    }
  }
  return cells;
}

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
  competitorZones: boolean;
  opportunityGrid: boolean;
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
    competitorZones: true,
    opportunityGrid: true,
  });
  
  const [viewState, setViewState] = useState({
    longitude: -98.5795,
    latitude: 39.8283,
    zoom: 4,
  });
  const liveViewStateRef = useRef(viewState);
  
  useEffect(() => {
    if (mapData?.center) {
      const centeredViewState = {
        longitude: mapData.center.lng,
        latitude: mapData.center.lat,
        zoom: 11,
      };
      setViewState(centeredViewState);
      liveViewStateRef.current = centeredViewState;
    }
  }, [mapData?.center]);
  
  const toggleLayer = useCallback((layer: keyof LayerState) => {
    setLayerState(prev => ({ ...prev, [layer]: !prev[layer] }));
  }, []);
  
  const heatmapGeoJSON = useMemo(() => ({
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
  }), [mapData?.layers?.heatmap?.data]);
  
  const polygonGeoJSON = useMemo(() => ({
    type: 'FeatureCollection' as const,
    features: (mapData?.layers?.polygons?.data || []).filter(g => g?.geometry?.type === 'Polygon'),
  }), [mapData?.layers?.polygons?.data]);
  
  const competitorZonesGeoJSON = useMemo(() => {
    const pins = mapData?.layers?.pins?.data || [];
    if (pins.length === 0) return { type: 'FeatureCollection' as const, features: [] };
    
    return {
      type: 'FeatureCollection' as const,
      features: pins.map((pin, idx) => ({
        type: 'Feature' as const,
        properties: { id: idx, name: pin.name },
        geometry: {
          type: 'Polygon' as const,
          coordinates: [createCirclePolygon(pin.lat, pin.lng, COMPETITOR_RADIUS_MILES)],
        },
      })),
    };
  }, [mapData?.layers?.pins?.data]);
  
  const opportunityGridGeoJSON = useMemo(() => {
    const pins = mapData?.layers?.pins?.data || [];
    const center = mapData?.center;
    if (pins.length === 0 || !center) return { type: 'FeatureCollection' as const, features: [] };
    
    const grid = generateOpportunityGrid(pins, center);
    const cellSizeLat = (GRID_RADIUS_MILES * 2 / 111) / GRID_SIZE;
    const cellSizeLng = (GRID_RADIUS_MILES * 2 / (111 * Math.cos(center.lat * Math.PI / 180))) / GRID_SIZE;
    
    return {
      type: 'FeatureCollection' as const,
      features: grid.map((cell, idx) => ({
        type: 'Feature' as const,
        properties: { 
          id: idx, 
          score: cell.score,
          minDistance: cell.minDistance.toFixed(2),
          inCompetitorZone: cell.inCompetitorZone,
        },
        geometry: {
          type: 'Polygon' as const,
          coordinates: [[
            [cell.lng - cellSizeLng/2, cell.lat - cellSizeLat/2],
            [cell.lng + cellSizeLng/2, cell.lat - cellSizeLat/2],
            [cell.lng + cellSizeLng/2, cell.lat + cellSizeLat/2],
            [cell.lng - cellSizeLng/2, cell.lat + cellSizeLat/2],
            [cell.lng - cellSizeLng/2, cell.lat - cellSizeLat/2],
          ]],
        },
      })),
    };
  }, [mapData?.layers?.pins?.data, mapData?.center]);
  
  const opportunityCount = useMemo(
    () => opportunityGridGeoJSON.features.filter(f => f.properties.score > 50).length,
    [opportunityGridGeoJSON]
  );
  
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
            onClick={() => toggleLayer('competitorZones')}
            className={`px-3 py-1.5 text-sm rounded-full flex items-center gap-1.5 transition-colors ${
              layerState.competitorZones 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-red-400"></span>
            Competitor Zones ({competitorZonesGeoJSON.features.length})
          </button>
          <button
            onClick={() => toggleLayer('opportunityGrid')}
            className={`px-3 py-1.5 text-sm rounded-full flex items-center gap-1.5 transition-colors ${
              layerState.opportunityGrid 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-green-400"></span>
            Opportunity Zones ({opportunityCount})
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
            onMove={(evt: ViewStateChangeEvent) => {
              liveViewStateRef.current = evt.viewState;
            }}
            onMoveEnd={(evt: ViewStateChangeEvent) => {
              liveViewStateRef.current = evt.viewState;
              setViewState(prev => {
                const next = liveViewStateRef.current;
                if (
                  prev.longitude === next.longitude &&
                  prev.latitude === next.latitude &&
                  prev.zoom === next.zoom
                ) {
                  return prev;
                }
                return {
                  longitude: next.longitude,
                  latitude: next.latitude,
                  zoom: next.zoom,
                };
              });
            }}
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
            
            {layerState.opportunityGrid && opportunityGridGeoJSON.features.length > 0 && (
              <Source id="opportunity-grid" type="geojson" data={opportunityGridGeoJSON}>
                <Layer
                  id="opportunity-grid-fill"
                  type="fill"
                  paint={{
                    'fill-color': [
                      'interpolate',
                      ['linear'],
                      ['get', 'score'],
                      0, 'rgba(158, 158, 158, 0.3)',
                      25, 'rgba(255, 235, 59, 0.4)',
                      50, 'rgba(205, 220, 57, 0.5)',
                      75, 'rgba(139, 195, 74, 0.6)',
                      100, 'rgba(46, 125, 50, 0.7)'
                    ],
                    'fill-opacity': 0.7,
                  }}
                />
                <Layer
                  id="opportunity-grid-outline"
                  type="line"
                  paint={{
                    'line-color': [
                      'case',
                      ['>', ['get', 'score'], 50], '#2E7D32',
                      '#9E9E9E'
                    ],
                    'line-width': 1,
                    'line-opacity': 0.6,
                  }}
                />
              </Source>
            )}
            
            {layerState.competitorZones && competitorZonesGeoJSON.features.length > 0 && (
              <Source id="competitor-zones" type="geojson" data={competitorZonesGeoJSON}>
                <Layer
                  id="competitor-zones-fill"
                  type="fill"
                  paint={{
                    'fill-color': 'rgba(244, 67, 54, 0.15)',
                    'fill-opacity': 0.4,
                  }}
                />
                <Layer
                  id="competitor-zones-outline"
                  type="line"
                  paint={{
                    'line-color': '#D32F2F',
                    'line-width': 2,
                    'line-dasharray': [2, 2],
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
