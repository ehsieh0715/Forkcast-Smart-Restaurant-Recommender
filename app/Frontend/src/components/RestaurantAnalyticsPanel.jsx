import RadarChart from "./RadarChart";

export default function RestaurantAnalyticsPanel() {
  return (
    <div className="h-full rounded-2xl border border-gray-200 p-5">
      <h1 className="mb-5 text-xl font-[500]">Visual Analytics Panel</h1>
      <div className="flex h-100 justify-center">
        <RadarChart />
      </div>
    </div>
  );
}
