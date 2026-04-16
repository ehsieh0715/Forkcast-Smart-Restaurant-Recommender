import { useRef, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

export default function MapboxMap() {
  const mapRef = useRef(null);
  const mapContainerRef = useRef(null);

  useEffect(() => {
    mapboxgl.accessToken =
      "pk.eyJ1IjoiYWFkaGl0aHlhMjMiLCJhIjoiY21jYnZ0eXZ3MDF3bjJoczMxNzNpaWM1NyJ9.hSJFXNFtVKbNdOPweiTpdA";

    // Initialize map
    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/light-v10",
      center: [-73.9712, 40.7831],
      zoom: 12,
    });

    // Load GeoJSON and add heat-style colored fill
    mapRef.current.on("load", async () => {
      const response = await fetch("/data/grid.geojson");
      const geojson = await response.json();

      mapRef.current.addSource("busyness", {
        type: "geojson",
        data: geojson,
      });

      mapRef.current.addLayer({
        id: "busyness-fill",
        type: "fill",
        source: "busyness",
        paint: {
          "fill-color": [
            "interpolate",
            ["linear"],
            ["get", "busyness_percentile"],
            0,
            "#FEB24C",
            0.1,
            "#FD8D3C",
            0.3,
            "#FC4E2A",
            0.5,
            "#E31A1C",
            0.7,
            "#BD0026",
            0.9,
            "#800026",
          ],
          "fill-opacity": 0.7,
        },
      });

      mapRef.current.addLayer({
        id: "busyness-outline",
        type: "line",
        source: "busyness",
        paint: {
          "line-color": "white",
          "line-width": 1,
        },
      });

      // Add popups
      mapRef.current.on("click", "busyness-fill", (e) => {
        const props = e.features[0].properties;
        const gridId = props.grid_id || "Unknown";
        const busyness = (props.busyness_percentile * 100).toFixed(1);

        new mapboxgl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(
            `<strong>Grid:</strong> ${gridId}<br/><strong>Busyness:</strong> ${busyness}%`,
          )
          .addTo(mapRef.current);
      });

      // Change cursor on hover
      mapRef.current.on("mouseenter", "busyness-fill", () => {
        mapRef.current.getCanvas().style.cursor = "pointer";
      });
      mapRef.current.on("mouseleave", "busyness-fill", () => {
        mapRef.current.getCanvas().style.cursor = "";
      });
    });

    return () => {
      if (mapRef.current) mapRef.current.remove();
    };
  }, []);

  return (
    <div className="h-[400px] w-full">
      <div ref={mapContainerRef} className="h-full w-full" />
    </div>
  );
}
