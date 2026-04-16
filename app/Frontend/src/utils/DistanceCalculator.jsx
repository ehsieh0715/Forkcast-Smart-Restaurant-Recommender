import { useEffect, useState } from "react";

export default function DistanceCalculator({
  userLocation,
  restaurantLocation,
}) {
  const [distance, setDistance] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userLocation || !restaurantLocation) return;

    const fetchDistance = async () => {
      try {
        const response = await fetch(
          "https://routes.googleapis.com/directions/v2:computeRoutes",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Goog-Api-Key": "AIzaSyCRB2HWkZIJVjwMxT3EqPnBa89OY4Bp8jI",
              "X-Goog-FieldMask": "routes.distanceMeters", // ✅ distance only
            },
            body: JSON.stringify({
              origin: {
                location: {
                  latLng: {
                    latitude: userLocation.lat,
                    longitude: userLocation.lng,
                  },
                },
              },
              destination: {
                location: {
                  latLng: {
                    latitude: restaurantLocation.lat,
                    longitude: restaurantLocation.lng,
                  },
                },
              },
              travelMode: "DRIVE",
            }),
          },
        );

        const data = await response.json();
        const route = data.routes?.[0];

        if (!route) throw new Error("No route returned");

        const km = (route.distanceMeters / 1000).toFixed(1);
        setDistance(`${km} km`);
      } catch (err) {
        console.error(err.message);
        setError("Distance unavailable");
      }
    };

    fetchDistance();
  }, [userLocation, restaurantLocation]);

  if (error) {
    return <span className="text-xs text-gray-500">{error}</span>;
  }

  if (!distance) {
    return <span className="text-xs text-gray-400">Calculating...</span>;
  }

  return <span>{distance}</span>;
}
