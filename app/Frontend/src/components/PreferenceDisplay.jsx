import {
  Star,
  MapPin,
  Users,
  DollarSign,
  Utensils,
  Notebook,
} from "lucide-react";

const priceMap = {
  1: "Cheap",
  2: "Medium",
  3: "Expensive",
};

const busynessMap = {
  1: { label: "Very Quiet", color: "text-green-500" },
  2: { label: "Quiet", color: "text-lime-500" },
  3: { label: "Moderate", color: "text-yellow-500" },
  4: { label: "Busy", color: "text-orange-500" },
  5: { label: "Very Busy", color: "text-red-500" },
};

const PreferenceDisplay = ({ preferences }) => {
  if (!preferences || Object.keys(preferences).length === 1) {
    return (
      <div className="m-5 flex flex-col items-center justify-center gap-2 rounded-2xl border border-gray-200 bg-white p-5 text-center text-sm text-gray-500 shadow-sm">
        <Notebook />
        <p>No preferences set yet.</p>
      </div>
    );
  }

  return (
    <div className="m-5 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-800">Preferences</h2>

      <ul className="space-y-3 text-xs text-gray-700">
        {preferences.cuisine_preferences?.length > 0 && (
          <li className="flex items-center gap-3">
            <Utensils className="h-4 w-4 text-[#636AE8]" />
            <span className="font-medium">Cuisine:</span>
            <span className="text-gray-600">
              {preferences.cuisine_preferences.join(", ")}
            </span>
          </li>
        )}

        {"distance_preference" in preferences && (
          <li className="flex items-center gap-3">
            <MapPin className="h-4 w-4 text-[#636AE8]" />
            <span className="font-medium">Max Distance:</span>
            <span className="text-gray-600">
              {preferences.distance_preference} m
            </span>
          </li>
        )}

        {"busyness_preference" in preferences && (
          <li className="flex items-center gap-3">
            <Users className="h-4 w-4 text-[#636AE8]" />
            <span className="font-medium">Busyness Tolerance:</span>
            <span
              className={`${busynessMap[preferences.busyness_preference].color}`}
            >
              {busynessMap[preferences.busyness_preference].label}
            </span>
          </li>
        )}

        {"minimum_rating" in preferences && (
          <li className="flex items-center gap-3">
            <Star className="h-4 w-4 text-[#636AE8]" />
            <span className="font-medium">Minimum Rating:</span>
            <span className="text-gray-600">{preferences.minimum_rating}</span>
          </li>
        )}

        {"price_level" in preferences && (
          <li className="flex items-center gap-3">
            <DollarSign className="h-4 w-4 text-[#636AE8]" />
            <span className="font-medium">Price Level:</span>
            <span className="text-gray-600">
              {priceMap[preferences.price_level] ?? "Unknown"}
            </span>
          </li>
        )}
      </ul>
    </div>
  );
};

export default PreferenceDisplay;
