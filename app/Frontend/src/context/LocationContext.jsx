import { createContext, useState } from "react";

export const LocationContext = createContext();

export default function LocationContextProvider({ children }) {
  const [location, setLocation] = useState(() => {
    const stored = localStorage.getItem("location");

    try {
      const parsed = stored ? JSON.parse(stored) : null;
      if (parsed?.latitude && parsed?.longitude)
        return { latitude: parsed.latitude, longitude: parsed.longitude };
    } catch (err) {
      console.error("Invalid location in localStorage", err);
    }

    return null;
  });

  const clearLocation = () => {
    setLocation(null);
  };

  return (
    <LocationContext.Provider value={{ location, setLocation, clearLocation }}>
      {children}
    </LocationContext.Provider>
  );
}
