import { Star } from "lucide-react";

export default function HomePageRestaurantCard({ data }) {
  return (
    <div className="rounded-2xl border-2 border-gray-200 shadow-lg">
      <img src={data.image} className="w-[100%]"></img>
      <div className="p-5">
        <p className="font-[600]">{data.title}</p>
        <p className="text-[13px] text-[#8C8D8B]">{data.description}</p>
      </div>
      <div className="m-auto w-[85%] border-b-1 border-b-[#EBEBEA]"></div>
      <div className="flex justify-between px-5 py-2">
        <div className="flex items-center gap-2 text-sm text-yellow-400">
          <Star className="h-4 w-4" />
          <p>{data.rating}</p>
        </div>
        <div>
          <p className="text-sm text-[#8C8D8B]">
            {data.price} . {data.distance} mi
          </p>
        </div>
      </div>
    </div>
  );
}
