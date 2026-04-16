import { Users } from "lucide-react";

export default function RestaurantCrowdForecast({ data }) {
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

  return (
    <div className="flex h-full flex-col justify-between rounded-2xl border border-gray-200 p-5">
      <h1 className="mb-5 text-xl font-[500]">Live and Forecasted Metrics</h1>

      <div className="text-xs font-[500] lg:text-sm">
        <div className="mb-2 flex items-center justify-between">
          <p>Crowd Level</p>
          <div className="flex items-center gap-2">
            <Users className={`${crowd.color} size-4`} />
            <span className={`${crowd.color}`}>{crowd.label}</span>
          </div>
        </div>

        <div className="flex gap-20">
          <div className="h-2 w-full rounded-full bg-gray-200">
            <div
              className={`h-2 rounded-full ${crowd.bar}`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </div>

      <p className="mt-5 text-xs text-[#8C8D8B]">
        Crowd and noise levels are estimated based on real-time data and
        historical patterns.
      </p>
    </div>
  );
}
