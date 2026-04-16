import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { OpenStreetMapProvider, GeoSearchControl } from "leaflet-geosearch";
import "leaflet-geosearch/dist/geosearch.css";

function SearchControl() {
  const map = useMap();

  useEffect(() => {
    const provider = new OpenStreetMapProvider();

    const searchControl = new GeoSearchControl({
      provider,
      style: "bar",
      showMarker: true,
      showPopup: false,
      autoClose: true,
      retainZoomLevel: false,
      animateZoom: false,
      keepResult: false,
    });

    map.addControl(searchControl);

    return () => map.removeControl(searchControl);
  }, [map]);

  return null;
}

export default function LeafletMap() {
  const [geoData, setGeoData] = useState(null);

  useEffect(() => {
    fetch("/data/grid.geojson")
      .then((res) => res.json())
      .then((data) => setGeoData(data));
  }, []);

  // Color scale function based on busyness percentile (0–1)
  const getColor = (value) => {
    const v = value * 100; // convert 0–1 to 0–100
    return v > 90
      ? "#800026"
      : v > 70
        ? "#BD0026"
        : v > 50
          ? "#E31A1C"
          : v > 30
            ? "#FC4E2A"
            : v > 10
              ? "#FD8D3C"
              : "#FEB24C";
  };

  // Style each feature based on its busyness_percentile
  const styleFeature = (feature) => {
    const value = feature.properties.busyness_percentile || 0;
    return {
      fillColor: getColor(value),
      weight: 1,
      opacity: 1,
      color: "white",
      fillOpacity: 0.7,
    };
  };

  const onEachDistrict = (feature, layer) => {
    const id = feature.properties?.grid_id || "Unknown";
    const percentile = feature.properties?.busyness_percentile || 0;
    layer.bindPopup(
      `<strong>Grid:</strong> ${id}<br/><strong>Busyness:</strong> ${(percentile * 100).toFixed(1)}%`,
    );
  };

  return (
    <div className="relative z-0 flex h-full w-full flex-col">
      <p className="my-5 text-2xl font-[700]">Busyness Heatmap</p>
      <div className="mb-5 flex items-center space-x-4 text-sm">
        <div className="relative">
          <input
            type="date"
            className="rounded-xl border-2 border-indigo-300 px-5 py-2 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
          />
        </div>

        <div className="relative">
          <input
            type="time"
            step="1"
            className="rounded-xl border-2 border-indigo-300 px-5 py-2 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
          />
        </div>
      </div>

      <MapContainer
        center={{ lat: 40.7831, lng: -73.9712 }}
        zoom={12}
        className="h-full w-full"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        <SearchControl />
        {geoData && (
          <GeoJSON
            data={geoData}
            style={styleFeature}
            onEachFeature={onEachDistrict}
          />
        )}
      </MapContainer>
    </div>
  );
}
