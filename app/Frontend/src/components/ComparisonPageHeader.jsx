import { useContext } from "react";
import { PlusCircleIcon } from "lucide-react";
import { RestaurantContext } from "../context/RestaurantContext";
import RestaurantSearchDropdown from "./RestaurantSearchDropdown";

export default function ComparisonPageHeader() {
  useContext(RestaurantContext);

  return (
    <header className="mx-10 my-10 rounded-2xl border border-gray-200 p-5">
      <h1 className="text-center text-xl font-[600] sm:text-left">
        Select Restaurants to compare
      </h1>

      <div className="mt-5 w-full">
        <RestaurantSearchDropdown mode="compare" />
      </div>
    </header>
  );
}
