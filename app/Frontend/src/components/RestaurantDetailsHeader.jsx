import { Star } from "lucide-react";
import { StarIcon as StarSolid } from "@heroicons/react/24/solid";
import { StarIcon as StarOutline } from "@heroicons/react/24/outline";

export default function RestaurantDetailsHeader({ data }) {
  const cuisines = data.cuisine_keyword?.map((c) => c.title) || [];

  const fullStars = Math.floor(data.rating);

  return (
    <>
      <img
        src={data.image_url ? data.image_url : "/no-image.jpg"}
        alt={data.full_name}
        className="mt-5 size-50 rounded-lg object-cover sm:hidden"
      />
      <div className="relative mt-5 flex items-center justify-between gap-6 rounded-2xl border border-gray-200 p-6">
        {/* Text Content */}
        <div className="flex-1">
          <h1 className="text-xl font-[700] capitalize md:text-2xl lg:text-3xl">
            {data.google_name?.toLowerCase() || data.full_name.toLowerCase()}
          </h1>
          <div className="my-2 flex items-center gap-1">
            {Array.from({ length: 5 }).map((_, index) => {
              const StarComponent = index < fullStars ? StarSolid : StarOutline;
              const color =
                index < fullStars ? "text-yellow-400" : "text-gray-400";
              return (
                <StarComponent className={`size-5 ${color}`} key={index} />
              );
            })}
            <p className="ml-1 text-sm font-[500] text-[#8C8D8B] lg:text-lg">
              ({data.review_count} Reviews)
            </p>
          </div>

          {cuisines.length > 0 && (
            <p className="text-sm font-[500] text-gray-400">
              {cuisines.join(", ")}
            </p>
          )}
          <p className="text-3xl font-[600] tracking-widest text-indigo-500">
            {"$".repeat(data.price_level ?? 0)}
          </p>
        </div>

        {/* Image */}
        <img
          src={data.image_url ? data.image_url : "/no-image.jpg"}
          alt={data.full_name}
          className="hidden size-50 rounded-lg object-cover sm:block"
        />
      </div>
    </>
  );
}
