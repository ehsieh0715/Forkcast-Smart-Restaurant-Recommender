import { createContext } from "react";
import { useState } from "react";

export const RestaurantContext = createContext();

export const RestaurantProvider = ({ children }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [allRestaurants, setAllRestaurants] = useState([]);

  const addRestaurant = (restaurant) => {
    setRestaurants((prev) => {
      if (prev.find((r) => r.restaurant_id === restaurant.restaurant_id))
        return prev;
      return [...prev, restaurant];
    });
  };

  const deleteRestaurant = (index) => {
    setRestaurants((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <RestaurantContext.Provider
      value={{
        restaurants,
        setRestaurants,
        addRestaurant,
        deleteRestaurant,
        allRestaurants, // ✅ Add this
        setAllRestaurants, // ✅ Add this
      }}
    >
      {children}
    </RestaurantContext.Provider>
  );
};
