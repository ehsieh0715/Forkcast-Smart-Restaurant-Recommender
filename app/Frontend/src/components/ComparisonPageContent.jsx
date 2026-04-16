import { useContext } from "react";
import ComparisonCard from "./ComparisonCard";
import { RestaurantContext } from "../context/RestaurantContext";

export default function ComparisonPageContent() {
  const { restaurants, deleteRestaurant } = useContext(RestaurantContext);

  return (
    <main className="mx-10 mt-5">
      <p className="text-center text-xl font-[700] sm:text-left">
        Side-by-Side Comparison
      </p>
      <div className="my-5 grid grid-cols-1 gap-10 md:grid-cols-2 lg:grid-cols-4">
        {restaurants.map((item, index) => (
          <ComparisonCard
            data={item}
            key={item.restaurant_id}
            deleteHandler={deleteRestaurant}
            index={index}
          />
        ))}
      </div>
    </main>
  );
}
