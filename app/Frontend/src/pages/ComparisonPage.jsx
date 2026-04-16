import { Suspense, useEffect } from "react";
import { Await, useLoaderData, redirect } from "react-router-dom";
import { RestaurantContext } from "../context/RestaurantContext";
import ComparisonPageContent from "../components/ComparisonPageContent";
import ComparisonPageHeader from "../components/ComparisonPageHeader";
import BackdropLoader from "../utils/BackdropLoader";
import { useContext } from "react";
import { getAuthToken } from "../components/Auth";
import { getOrCreateSession } from "../utils/Session";

export default function ComparisonPage() {
  const restaurantData = useLoaderData();
  useContext(RestaurantContext);

  return (
    <Suspense fallback={<BackdropLoader />}>
      <Await resolve={restaurantData.restaurants}>
        {(resolvedRestaurants) => (
          <ResolvedRestaurants resolvedRestaurants={resolvedRestaurants} />
        )}
      </Await>
    </Suspense>
  );
}

function ResolvedRestaurants({ resolvedRestaurants }) {
  const { setRestaurants, restaurants } = useContext(RestaurantContext);

  // Set context on mount
  useEffect(() => {
    setRestaurants(resolvedRestaurants);
  }, [resolvedRestaurants, setRestaurants]);

  return (
    <>
      <ComparisonPageHeader />
      {restaurants.length > 0 && <ComparisonPageContent />}
    </>
  );
}

export function loader() {
  const token = getAuthToken();
  if (!token) return redirect("/");

  const userId = localStorage.getItem("user");

  const restaurants = new Promise(async (resolve, reject) => {
    try {
      const sessionId = await getOrCreateSession(userId);

      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/comparison/session/${sessionId}/view`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ user_id: userId }),
        },
      );

      if (!res.ok) {
        reject(
          new Response("Failed to load restaurants", {
            status: res.status,
          }),
        );
        return;
      }

      const result = await res.json();
      resolve(result.restaurants);
    } catch (err) {
      reject(
        new Response("Error loading comparison data", {
          status: 500,
          statusText: err.message,
        }),
      );
    }
  });

  return { restaurants };
}
