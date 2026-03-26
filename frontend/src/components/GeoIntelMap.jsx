import { useEffect, useMemo, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.heat';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const statusColor = {
  pending: '#f59e0b',
  working: '#0ea5e9',
  completed: '#22c55e',
};

const buildPopup = (point) => {
  const location = [point.city, point.district, point.state].filter(Boolean).join(', ');
  const createdAt = point.created_at ? new Date(point.created_at).toLocaleString() : 'Unknown';
  return `
    <div style="min-width:220px;max-width:280px;line-height:1.4;">
      <div style="font-weight:700;font-size:14px;margin-bottom:6px;">${point.title || 'Citizen Report'}</div>
      <div style="font-size:12px;margin-bottom:4px;"><b>Type:</b> ${point.report_type || 'Unknown'}</div>
      <div style="font-size:12px;margin-bottom:4px;"><b>Status:</b> ${point.status || 'pending'}</div>
      <div style="font-size:12px;margin-bottom:4px;"><b>Region:</b> ${location || 'Unknown'}</div>
      <div style="font-size:12px;"><b>Created:</b> ${createdAt}</div>
    </div>
  `;
};

const pointWeight = (point) => {
  if (point.priority === 'high') return 1;
  if (point.priority === 'medium') return 0.7;
  return 0.45;
};

const GeoIntelMap = ({
  points,
  clusters,
  regionGeoJson,
  loading,
  showHeatmap,
  onBoundsChange,
  onReportClick,
}) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const clusterLayerRef = useRef(null);
  const clusterCenterLayerRef = useRef(null);
  const heatLayerRef = useRef(null);
  const regionLayerRef = useRef(null);

  const normalizedPoints = useMemo(() => {
    return (points || []).filter(
      (point) => typeof point.latitude === 'number' && typeof point.longitude === 'number'
    );
  }, [points]);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) {
      return;
    }

    const map = L.map(mapContainerRef.current, {
      center: [22.9734, 78.6569],
      zoom: 5,
      zoomControl: true,
      preferCanvas: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    const clusterLayer = L.markerClusterGroup({
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      removeOutsideVisibleBounds: true,
    });

    clusterLayerRef.current = clusterLayer;
    clusterLayer.addTo(map);

    map.on('moveend', () => {
      if (!onBoundsChange) return;
      const bounds = map.getBounds();
      const bbox = [
        bounds.getWest().toFixed(6),
        bounds.getSouth().toFixed(6),
        bounds.getEast().toFixed(6),
        bounds.getNorth().toFixed(6),
      ].join(',');
      onBoundsChange(bbox);
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
      clusterLayerRef.current = null;
      clusterCenterLayerRef.current = null;
      heatLayerRef.current = null;
      regionLayerRef.current = null;
    };
  }, [onBoundsChange]);

  const getIntensityColor = (intensity) => {
    if (intensity >= 0.8) return '#b91c1c';
    if (intensity >= 0.6) return '#dc2626';
    if (intensity >= 0.4) return '#f97316';
    if (intensity >= 0.2) return '#f59e0b';
    return '#facc15';
  };

  useEffect(() => {
    if (!mapRef.current || !clusterLayerRef.current) {
      return;
    }

    const map = mapRef.current;
    const clusterLayer = clusterLayerRef.current;

    clusterLayer.clearLayers();

    normalizedPoints.forEach((point) => {
      const marker = L.circleMarker([point.latitude, point.longitude], {
        radius: 7,
        fillColor: statusColor[point.status] || '#ef4444',
        color: '#ffffff',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.9,
      });

      marker.bindPopup(buildPopup(point));
      if (onReportClick) {
        marker.on('click', () => onReportClick(point));
      }
      clusterLayer.addLayer(marker);
    });

    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }

    if (showHeatmap && normalizedPoints.length > 0) {
      const heatData = normalizedPoints.map((point) => [point.latitude, point.longitude, pointWeight(point)]);
      heatLayerRef.current = L.heatLayer(heatData, {
        radius: 22,
        blur: 16,
        maxZoom: 12,
        minOpacity: 0.35,
      });
      heatLayerRef.current.addTo(map);
    }
  }, [normalizedPoints, showHeatmap, onReportClick]);

  useEffect(() => {
    if (!mapRef.current) {
      return;
    }

    const map = mapRef.current;

    if (regionLayerRef.current) {
      map.removeLayer(regionLayerRef.current);
      regionLayerRef.current = null;
    }

    if (clusterCenterLayerRef.current) {
      map.removeLayer(clusterCenterLayerRef.current);
      clusterCenterLayerRef.current = null;
    }

    if (regionGeoJson?.features?.length) {
      regionLayerRef.current = L.geoJSON(regionGeoJson, {
        style: (feature) => {
          const intensity = feature?.properties?.intensity || 0;
          return {
            color: '#ffffff',
            weight: 1,
            fillColor: getIntensityColor(intensity),
            fillOpacity: 0.24,
          };
        },
        onEachFeature: (feature, layer) => {
          const props = feature.properties || {};
          layer.bindPopup(`
            <div style="min-width:200px;line-height:1.35;">
              <div style="font-weight:700;margin-bottom:4px;">${props.region || 'Unknown Region'}</div>
              <div style="font-size:12px;"><b>Incidents:</b> ${props.count || 0}</div>
              <div style="font-size:12px;"><b>Intensity:</b> ${Math.round((props.intensity || 0) * 100)}%</div>
              <div style="font-size:12px;"><b>Overlay radius:</b> ${props.radius_km || 0} km</div>
              <div style="font-size:11px;margin-top:4px;color:#475569;">Insight: region color indicates incident concentration.</div>
            </div>
          `);
        },
      });
      regionLayerRef.current.addTo(map);
    }

    if (clusters?.length) {
      const group = L.layerGroup();
      clusters.slice(0, 15).forEach((cluster) => {
        const center = cluster.center || {};
        if (typeof center.latitude !== 'number' || typeof center.longitude !== 'number') {
          return;
        }

        const marker = L.circleMarker([center.latitude, center.longitude], {
          radius: 9,
          color: '#7c2d12',
          fillColor: '#fb923c',
          fillOpacity: 0.95,
          weight: 2,
        });
        marker.bindPopup(`
          <div style="min-width:220px;line-height:1.35;">
            <div style="font-weight:700;margin-bottom:4px;">Cluster #${cluster.cluster_id}</div>
            <div style="font-size:12px;"><b>Incidents:</b> ${cluster.size}</div>
            <div style="font-size:12px;"><b>Density:</b> ${cluster.density_per_km2}/km²</div>
            <div style="font-size:12px;"><b>Area:</b> ${cluster.area_km2} km²</div>
            <div style="font-size:11px;margin-top:4px;color:#475569;">Insight: dense clusters indicate concentrated operational pressure.</div>
          </div>
        `);
        group.addLayer(marker);
      });
      clusterCenterLayerRef.current = group;
      clusterCenterLayerRef.current.addTo(map);
    }
  }, [clusters, regionGeoJson]);

  return (
    <div className="relative w-full h-[500px] rounded-xl overflow-hidden border border-slate-200">
      {loading && (
        <div className="absolute inset-0 z-[500] bg-white/75 backdrop-blur-sm flex items-center justify-center text-sm font-semibold text-slate-700">
          Loading map intelligence...
        </div>
      )}
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};

export default GeoIntelMap;
