import { Clock } from "lucide-react";

export default function RestaurantWaittimes({ data }) {
  return (
    <div className="h-full rounded-2xl border border-gray-200 p-5">
      <h1 className="mb-5 text-xl font-[500]">Opening Hours</h1>

      {Object.keys(data.opening_hours || {}).length === 0 && (
        <p>Unavailable currently!</p>
      )}

      {Object.keys(data.opening_hours || {}).length !== 0 && (
        <div className="flex flex-col gap-2 px-5">
          {Object.entries(data.opening_hours).map(([day, times]) => (
            <div key={day} className="flex justify-between text-sm">
              <span className="font-[500] capitalize">{day}</span>
              <span className="text-[#8C8D8B]">{times.join(", ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
