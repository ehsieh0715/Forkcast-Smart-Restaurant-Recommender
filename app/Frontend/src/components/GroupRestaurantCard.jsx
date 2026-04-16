import { Star, MapPin, Clock } from "lucide-react";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { RestaurantContext } from "./../context/RestaurantContext";

export default function GroupRestaurantCard({ data }) {
  const { addRestaurant } = useContext(RestaurantContext);
  const navigate = useNavigate();

  // Convert meters to miles (1 mile ≈ 1609.34 meters)
  const distanceInMiles = (data.distance_meters / 1609.34).toFixed(2);

  return (
    <div className="rounded-2xl border border-gray-200 shadow-lg">
      <div
        className="flex h-[200px] w-full justify-between rounded-t-xl bg-cover bg-center"
        style={{
          backgroundImage: `url(${data.image || "/placeholder.jpg"})`,
        }}
      >
        <p className="m-5 self-end font-[600] text-white">
          {data.full_name}
        </p>
        <p className="m-3 self-start rounded-2xl bg-[#636AE8] px-4 py-1 text-sm font-[600] text-white">
          Match : {(data.fit_score * 100).toFixed(0)}%
        </p>
      </div>

      <div className="flex justify-around p-4">
        <div className="flex items-center gap-2 text-sm text-yellow-400">
          <Star className="size-3" />
          <p>{data.rating}</p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <MapPin className="size-3 text-gray-500" />
          <p className="text-sm text-[#8C8D8B]">{distanceInMiles} mi</p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Clock className="size-3 text-gray-500" />
          <p className="text-sm text-[#8C8D8B]">
            {/* Placeholder since no wait time is provided */}
            ~10 mins
          </p>
        </div>
      </div>

      <div className="mb-5 flex flex-col items-center justify-center font-[500] max-md:mt-3 sm:flex-row sm:gap-5">
        <button
          onClick={() => {
            addRestaurant(data);
            navigate("/compare");
          }}
          className="my-2 w-[40%] max-w-[200px] cursor-pointer rounded-lg border-2 border-[#E8618C] bg-[#E8618C] px-4 py-2 text-center text-sm text-white transition-colors duration-200 ease-in hover:bg-white hover:text-[#E8618C]"
        >
          Vote
        </button>
        <button
          onClick={() => {
            addRestaurant(data);
            navigate("/compare");
          }}
          className="my-2 w-[40%] max-w-[200px] cursor-pointer rounded-lg border-2 border-indigo-500 bg-[#636AE8] px-4 py-2 text-center text-sm text-white transition-colors duration-200 ease-in hover:bg-white hover:text-indigo-500"
        >
          Compare
        </button>
      </div>
    </div>
  );
}
