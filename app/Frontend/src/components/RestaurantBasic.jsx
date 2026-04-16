import { MapPin, Phone, TrendingUp } from "lucide-react";
import DistanceCalculator from "../utils/DistanceCalculator";

export default function RestaurantBasic({ data }) {
  function getUserLocation() {
    try {
      const stored = JSON.parse(localStorage.getItem("location"));
      if (stored?.latitude && stored?.longitude) {
        return { lat: stored.latitude, lng: stored.longitude };
      }
    } catch {
      return null;
    }
  }

  return (
    <div className="h-full rounded-2xl border border-gray-200 p-5">
      <h1 className="mb-5 text-xl font-[500]">Basic Information</h1>
      <div className="flex flex-col gap-3 text-sm">
        <div className="flex items-center gap-2">
          <MapPin className="size-4 text-blue-400" />
          <p className="font-[400]">
            Address:{" "}
            <span className="text-[#8C8D8B]">
              {data.address || "Unavailable"}
            </span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Phone className="size-4 text-blue-400" />
          <p className="font-[400]">
            Contact:{" "}
            <span className="text-[#8C8D8B]">
              {data.phone || "Unavailable"}
            </span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <TrendingUp className="size-4 text-blue-400" />
          <p className="font-[400]">
            Distance:{" "}
            <span className="text-[#8C8D8B]">
              <DistanceCalculator
                userLocation={getUserLocation()}
                restaurantLocation={{ lat: data.lat, lng: data.lon }}
                travelMode="DRIVE"
              />
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
