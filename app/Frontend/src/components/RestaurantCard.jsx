import { Link } from "react-router-dom";
import { Star, Users, MessageCircle, DollarSign, ImageOff } from "lucide-react";
import { motion as Motion } from "framer-motion";
import { useContext } from "react";
import { HeatmapContext } from "../context/HeatmapContext";
import { StarIcon as StarSolid } from "@heroicons/react/24/solid";
import { StarIcon as StarOutline } from "@heroicons/react/24/outline";

export default function RestaurantCard({ data }) {
  const rating = Math.floor(data.rating);

  const { datetime } = useContext(HeatmapContext);

  const busynessMap = {
    1: { label: "Very Quiet", color: "text-green-500" },
    2: { label: "Quiet", color: "text-lime-500" },
    3: { label: "Moderate", color: "text-yellow-500" },
    4: { label: "Busy", color: "text-orange-500" },
    5: { label: "Very Busy", color: "text-red-500" },
  };

  const { label: busyness, color } = busynessMap[
    data.predicted_busyness || data.predicted_level
  ] || {
    label: "Unknown",
    color: "text-gray-500",
  };

  const fitScore = data.fit_score
    ? `${Math.round(data.fit_score * 100)}%`
    : null;

  const name = data.name?.toLowerCase() || data.full_name?.toLowerCase();

  const priceLabel =
    data.price_level === 1
      ? "Cheap"
      : data.price_level === 2
        ? "Medium"
        : data.price_level === 3
          ? "Expensive"
          : "Unavailable";

  return (
    <Motion.div
      whileHover={{ scale: 1.1 }}
      className="group relative flex h-[450px] max-h-[450px] w-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md"
    >
      {/* Image Section */}
      <div className="relative h-[160px] w-full overflow-hidden bg-gray-100">
        {data.image_url ? (
          <div
            className="h-full w-full bg-cover bg-center"
            style={{ backgroundImage: `url(${data.image_url})` }}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <ImageOff className="h-10 w-10 text-gray-300" />
          </div>
        )}

        {fitScore && (
          <div className="absolute top-2 right-2 rounded-full bg-[#636AE8] px-3 py-1 text-xs font-semibold text-white shadow-sm">
            Match: {fitScore}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col justify-between p-4">
        {/* Name */}
        <h2 className="truncate text-base font-semibold text-gray-800 capitalize">
          {name}
        </h2>

        {/* Rating */}
        <div className="mt-2 flex items-center gap-1">
          {[...Array(5)].map((_, i) =>
            i < rating ? (
              <StarSolid key={i} className="size-4 text-yellow-400" />
            ) : (
              <StarOutline key={i} className="h-4 w-4 text-gray-300" />
            ),
          )}
          <span className="ml-1 text-sm text-gray-600">{data.rating}</span>
        </div>

        {/* Reviews */}
        <div className="mt-1 flex items-center gap-2 text-sm text-[#8C8D8B]">
          <MessageCircle className="size-4 text-gray-400" />
          Reviews: {data.review_count}
        </div>

        {/* Price */}
        <div className="mt-1 flex items-center gap-2 text-sm text-[#8C8D8B]">
          <DollarSign className="size-4 text-gray-400" />
          {priceLabel}
        </div>

        {/* Busyness */}
        <div className="mt-1 flex items-center gap-2 text-sm">
          <Users className={`size-4 ${color}`} />
          <span className={`font-semibold ${color}`}>{busyness}</span>
        </div>

        {/* CTA Button */}
        <div className="mt-4">
          <Link
            to={
              datetime
                ? `/restaurant/${datetime}/${data.restaurant_id}`
                : `/restaurant/${data.restaurant_id}`
            }
            className="block w-full rounded-md border border-[#636AE8]/30 bg-white px-4 py-2 text-center text-sm font-semibold text-[#636AE8]"
          >
            View details
          </Link>
        </div>
      </div>
    </Motion.div>
  );
}
