import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

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
  onBoundsChange?: (bounds: any) => void;
}

const businessIcon = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  
  useEffect(() => {
    if (center[0] !== 0 && center[1] !== 0) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  
  return null;
}

function HeatmapLayer({ points }: { points: HeatmapPoint[] }) {
  const map = useMap();
  const heatLayerRef = useRef<any>(null);
  
  useEffect(() => {
    if (typeof window !== 'undefined' && points.length > 0) {
      import('leaflet.heat').then(() => {
        if (heatLayerRef.current) {
          map.removeLayer(heatLayerRef.current);
        }
        
        const heatData = points.map(p => [p.lat, p.lng, p.intensity]);
        heatLayerRef.current = (L as any).heatLayer(heatData, {
          radius: 25,
          blur: 15,
          maxZoom: 17,
          gradient: { 0.4: 'blue', 0.6: 'yellow', 1: 'red' }
        }).addTo(map);
      });
    }
    
    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
    };
  }, [points, map]);
  
  return null;
}

export default function ConsultantMap({ mapData, city, isLoading, onBoundsChange }: ConsultantMapProps) {
  const [layerState, setLayerState] = useState<LayerState>({
    pins: true,
    heatmap: true,
    polygons: true,
  });
  
  const defaultCenter: [number, number] = [39.8283, -98.5795];
  const defaultZoom = 4;
  
  const center: [number, number] = mapData?.center 
    ? [mapData.center.lat, mapData.center.lng]
    : defaultCenter;
  
  const zoom = mapData?.center ? 11 : defaultZoom;
  
  const toggleLayer = (layer: keyof LayerState) => {
    setLayerState(prev => ({ ...prev, [layer]: !prev[layer] }));
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
  
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3 px-2">
        <div className="flex gap-2">
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
      
      <div className="rounded-lg overflow-hidden border border-gray-200 shadow-sm">
        <MapContainer
          center={center}
          zoom={zoom}
          style={{ height: '500px', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <MapController center={center} zoom={zoom} />
          
          {layerState.pins && mapData?.layers?.pins?.data?.map((pin) => (
            <Marker 
              key={`pin-${pin.id}`} 
              position={[pin.lat, pin.lng]}
              icon={pin.source === 'yelp' ? redIcon : businessIcon}
            >
              <Popup>
                <div className="min-w-[200px]">
                  <h3 className="font-semibold text-gray-900">{pin.name}</h3>
                  {pin.rating && (
                    <div className="flex items-center gap-1 mt-1">
                      <span className="text-yellow-500">★</span>
                      <span>{pin.rating}</span>
                      {pin.reviews && <span className="text-gray-500">({pin.reviews} reviews)</span>}
                    </div>
                  )}
                  <div className="mt-2 text-xs text-gray-500 capitalize">
                    Source: {pin.source?.replace('_', ' ')}
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
          
          {layerState.heatmap && mapData?.layers?.heatmap?.data && (
            <HeatmapLayer points={mapData.layers.heatmap.data} />
          )}
          
          {layerState.polygons && mapData?.layers?.polygons?.data?.map((geojson, idx) => {
            if (geojson?.geometry?.type === 'Polygon') {
              const positions = geojson.geometry.coordinates[0].map(
                (coord: number[]) => [coord[1], coord[0]] as [number, number]
              );
              return (
                <Polygon
                  key={`poly-${idx}`}
                  positions={positions}
                  pathOptions={{
                    fillColor: '#9C27B0',
                    fillOpacity: 0.2,
                    color: '#7B1FA2',
                    weight: 2,
                  }}
                >
                  {geojson.properties && (
                    <Popup>
                      <div>
                        <h3 className="font-semibold">{geojson.properties.neighborhood || 'Neighborhood'}</h3>
                        {geojson.properties.post_density && (
                          <p className="text-sm">Activity: {geojson.properties.post_density} posts</p>
                        )}
                      </div>
                    </Popup>
                  )}
                </Polygon>
              );
            }
            return null;
          })}
        </MapContainer>
      </div>
      
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
