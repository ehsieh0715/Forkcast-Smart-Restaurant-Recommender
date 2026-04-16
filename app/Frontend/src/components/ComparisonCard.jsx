import {
  CircleCheck,
  CircleX,
  DollarSign,
  MapPin,
  Star,
  Users,
  Utensils,
  X,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
import { toast } from "react-hot-toast";
import DistanceCalculator from "../utils/DistanceCalculator";
import { useContext } from "react";
import { HeatmapContext } from "./../context/HeatmapContext";
import { StarIcon as StarSolid } from "@heroicons/react/24/solid";

export default function ComparisonCard({ data, deleteHandler, index }) {
  const [loading, setLoading] = useState(false);
  const { datetime } = useContext(HeatmapContext);

  const level = data.predicted_level || 1;

  const busynessMap = {
    1: { label: "Very Quiet", color: "text-green-500", bar: "bg-green-500" },
    2: { label: "Quiet", color: "text-lime-500", bar: "bg-lime-500" },
    3: { label: "Moderate", color: "text-yellow-500", bar: "bg-yellow-500" },
    4: { label: "Busy", color: "text-orange-500", bar: "bg-orange-500" },
    5: { label: "Very Busy", color: "text-red-500", bar: "bg-red-500" },
  };

  const crowd = busynessMap[level] || busynessMap[1];
  const percentage = level * 20;

  const handleRemove = async () => {
    const sessionId = localStorage.getItem("sessionId");
    const userId = localStorage.getItem("user");

    if (!sessionId || !userId || !data.restaurant_id) {
      toast.error("Missing session, user, or restaurant ID.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/comparison/session/${sessionId}/remove_restaurant`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: userId,
            restaurant_id: data.restaurant_id,
          }),
        },
      );

      const result = await res.json();

      if (!res.ok) {
        throw new Error(result.message || "Failed to remove restaurant.");
      }

      toast.success("Removed from comparison.");
      deleteHandler(index);
    } catch (err) {
      console.error(err);
      toast.error(err.message || "Error removing restaurant.");
    } finally {
      setLoading(false);
    }
  };

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
    <div className="relative flex flex-col gap-3 rounded-2xl border border-gray-200 p-5 text-xs">
      {/* X icon */}
      <div className="flex justify-between">
        <span className="text-sm font-[600] capitalize">
          {data.google_name?.toLowerCase() || data.full_name.toLowerCase()}
        </span>
        <button
          className="cursor-pointer disabled:cursor-not-allowed"
          onClick={handleRemove}
          disabled={loading}
          title="Remove"
        >
          <X
            className={`size-4 transition ${
              loading ? "text-gray-300" : "text-gray-500 hover:text-red-500"
            }`}
          />
        </button>
      </div>

      {/* Image */}
      <div className="relative">
        <img
          src={data.image_url || "no-image.jpg"}
          className="m-auto h-60 w-full rounded-lg object-cover"
          alt={data.full_name}
        />
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-white/60">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-indigo-500"></div>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <StarSolid className="size-4 text-yellow-400" />
        <p>{data.rating}</p>
        <span className="text-[#8C8D8B]">({data.review_count} reviews)</span>
      </div>

      <div className="flex items-center gap-2">
        <Utensils className="size-4 text-gray-500" />
        <p className="font-medium">Cuisine:</p>
        <span className="text-[#8C8D8B]">
          {data.cuisine_keyword?.map((c) => c.title).join(", ")}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <DollarSign className="size-4 text-gray-400" />
        <p className="text-[12px] text-[#8C8D8B]">
          {data.price_level === 1
            ? "Cheap"
            : data.price_level === 2
              ? "Medium"
              : data.price_level === 3
                ? "Expensive"
                : "Unknown"}
        </p>
      </div>

      <div className="flex items-center gap-2">
        <MapPin className="size-4 text-gray-400" />
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

      <div className="text-xs font-[500]">
        <div className="mb-2 flex items-center justify-between">
          <p>Crowd Level</p>
          <div className="flex items-center gap-2">
            <Users className={`size-4 ${crowd.color}`} />
            <span className={`${crowd.color} text-xs font-[700]`}>
              {crowd.label}
            </span>
          </div>
        </div>

        <div className="h-2 w-full rounded-full bg-gray-200">
          <div
            className={`h-2 rounded-full ${crowd.bar}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>

      <Link
        to={
          datetime
            ? `/restaurant/${datetime}/${data.restaurant_id}`
            : `/restaurant/${data.restaurant_id}`
        }
        className="mt-3 cursor-pointer border border-gray-200 p-2 text-center font-[500] transition-all duration-200 ease-in hover:bg-gray-100"
      >
        View Details
      </Link>
    </div>
  );
}
