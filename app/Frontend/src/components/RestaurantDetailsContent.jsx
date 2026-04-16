import RestaurantBasic from "./RestaurantBasic";
import RestaurantCrowdForecast from "./RestaurantCrowdForecast";
import RestaurantWaittimes from "./RestaurantWaittimes";
import RestaurantAmenities from "./RestaurantAmenities";
import RestaurantActions from "./RestaurantActions";

export default function RestaurantDetailsContent({ data }) {
  return (
    <div className="my-10 grid auto-rows-auto grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
      <div className="lg:row-span-3">
        <RestaurantBasic data={data} />
      </div>

      <div className="lg:row-span-3">
        <RestaurantWaittimes data={data} />
      </div>
      <div className="lg:row-span-3">
        <RestaurantAmenities data={data} />
      </div>
      <div className="lg:col-span-2 lg:row-span-2">
        <RestaurantCrowdForecast data={data} />
      </div>
      <div className="lg:row-span-2">
        <RestaurantActions data={data} />
      </div>
    </div>
  );
}
