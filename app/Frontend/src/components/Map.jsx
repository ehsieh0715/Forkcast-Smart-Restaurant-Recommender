import { useContext, useEffect, useRef } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { LocationContext } from "../context/LocationContext";
import { HeatmapContext } from "../context/HeatmapContext";

export default function Map({ mode = "busy" }) {
  const mapRef = useRef(null);
  const inputRef = useRef(null);
  const markerRef = useRef(null);
  const infoWindowRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const hasCenteredRef = useRef(false);

  const { location, setLocation } = useContext(LocationContext);
  const { geoJsonData } = useContext(HeatmapContext);

  useEffect(() => {
    const map = mapInstanceRef.current;

    if (mode === "busy" && map && geoJsonData && map.data) {
      // Clear previous data
      map.data.forEach((feature) => {
        map.data.remove(feature);
      });

      try {
        map.data.addGeoJson(geoJsonData);
      } catch (err) {
        console.error("Failed to load GeoJSON into map:", err);
      }
    }
  }, [mapInstanceRef.current, geoJsonData, mode]);

  useEffect(() => {
    const loadMap = async () => {
      const loader = new Loader({
        apiKey: "AIzaSyCRB2HWkZIJVjwMxT3EqPnBa89OY4Bp8jI",
        version: "weekly",
        libraries: ["places"],
      });

      await loader.load();
      const { Map } = await google.maps.importLibrary("maps");

      const initialCenter =
        location?.latitude && location?.longitude
          ? { lat: location.latitude, lng: location.longitude }
          : { lat: 40.7831, lng: -73.9712 };

      const map = new Map(mapRef.current, {
        center: initialCenter,
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: true,
        zoomControl: true,
      });

      mapInstanceRef.current = map;

      // Place marker immediately if location exists
      if (location?.latitude && location?.longitude) {
        const latLng = new google.maps.LatLng(
          location.latitude,
          location.longitude,
        );
        map.setCenter(latLng);
        map.setZoom(14);
        placeMarker(latLng);
        hasCenteredRef.current = true;
      }

      map.data.setStyle((feature) => {
        const level = feature.getProperty("predicted_level") || 0;
        const colorMap = {
          5: "#ef4444",
          4: "#f97316",
          3: "#eab308",
          2: "#84cc16",
          1: "#22c55e",
        };
        return {
          fillColor: colorMap[level] || "#d1d5db",
          fillOpacity: 0.6,
          strokeColor: "#ffffff",
          strokeWeight: 1,
        };
      });

      const infoWindow = new google.maps.InfoWindow({ maxWidth: 250 });
      infoWindowRef.current = infoWindow;

      map.data.addListener("click", (event) => {
        const level = event.feature.getProperty("predicted_level");
        const grid = event.feature.getProperty("grid_id");

        const content = `
  <div style="
    font-family: 'Inter', sans-serif;
    background: white;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    max-width: 240px;
  ">
    <div style="
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #111827;
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 4px;
    ">
      📍 Grid ID: <span style="color: #3b82f6;">${grid}</span>
    </div>
    <div style="
      font-size: 14px;
      color: #374151;
      display: flex;
      justify-content: space-between;
      align-items: center;
    ">
      <span>Predicted Busyness:</span>
      <span style="
        font-weight: 600;
        background: ${
          level >= 5
            ? "#ef4444"
            : level === 4
              ? "#f97316"
              : level === 3
                ? "#eab308"
                : level === 2
                  ? "#84cc16"
                  : "#22c55e"
        };
        color: white;
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 12px;
        margin-left:4px;
      ">
        Level ${level}
      </span>
    </div>
  </div>
`;
        infoWindow.setContent(content);
        infoWindow.setPosition(event.latLng);
        infoWindow.open(map);

        placeMarker(event.latLng);
      });

      map.addListener("click", (e) => {
        placeMarker(e.latLng);
      });

      const autocomplete = new google.maps.places.Autocomplete(
        inputRef.current,
        {
          fields: ["geometry"],
        },
      );

      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) return;

        const loc = place.geometry.location;
        map.setCenter(loc);
        map.setZoom(14);
        placeMarker(loc);
      });
    };

    loadMap();
  }, []);

  useEffect(() => {
    if (!location || hasCenteredRef.current || !mapInstanceRef.current) return;

    const latLng = new google.maps.LatLng(
      location.latitude,
      location.longitude,
    );

    setTimeout(() => {
      mapInstanceRef.current.setCenter(latLng);
      mapInstanceRef.current.setZoom(14);
      placeMarker(latLng);
      hasCenteredRef.current = true;
    }, 300); // allow map to finish rendering
  }, [location]);

  const placeMarker = (latLng) => {
    const map = mapInstanceRef.current;
    if (!map) {
      console.warn("Map not initialized when placing marker");
      return;
    }

    if (!markerRef.current) {
      markerRef.current = new google.maps.Marker({
        map,
        position: latLng,
      });
    } else {
      markerRef.current.setPosition(latLng);
    }

    setLocation({
      latitude: latLng.lat(),
      longitude: latLng.lng(),
    });
  };

  return (
    <div className="relative z-0 flex h-full w-full flex-col">
      {mode !== "locate" && (
        <p className="my-5 text-2xl font-[700]">Busyness Heatmap</p>
      )}

      <div className="relative h-full w-full">
        <input
          ref={inputRef}
          type="text"
          placeholder="Search places..."
          className="absolute top-4 left-4 z-10 w-72 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-md focus:border-indigo-500 focus:outline-none"
        />
        <div ref={mapRef} className="h-full w-full" />
      </div>
    </div>
  );
}
