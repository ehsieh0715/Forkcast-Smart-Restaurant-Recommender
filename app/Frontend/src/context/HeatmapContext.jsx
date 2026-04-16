import { createContext, useState, useEffect } from "react";

export const HeatmapContext = createContext();

function getRoundedLocalTimeStringWithZ() {
  const now = new Date();
  now.setMinutes(0, 0, 0); // round to top of the hour

  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hour = String(now.getHours()).padStart(2, "0");

  return `${year}-${month}-${day}T${hour}:00:00.000Z`;
}

export default function HeatmapProvider({ children }) {
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ✅ Set initial datetime to local time with 'Z' suffix but no timezone shift
  const [datetime, setDatetime] = useState(getRoundedLocalTimeStringWithZ());

  const fetchHeatmapData = async (datetimeISO = null) => {
    try {
      setLoading(true);

      let url = `${import.meta.env.VITE_API_URL}/heatmap`;
      if (datetimeISO) {
        url += `?requested_time=${encodeURIComponent(datetimeISO)}`;
      }

      const response = await fetch(url);
      const geojson = await response.json();
      setGeoJsonData(geojson);
    } catch (err) {
      console.error("Failed to fetch heatmap GeoJSON:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHeatmapData(datetime);
  }, [datetime]);

  return (
    <HeatmapContext.Provider
      value={{
        geoJsonData,
        setGeoJsonData,
        loading,
        error,
        refetch: fetchHeatmapData,
        setDatetime,
        datetime,
      }}
    >
      {children}
    </HeatmapContext.Provider>
  );
}
