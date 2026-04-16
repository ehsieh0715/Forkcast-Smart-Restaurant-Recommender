import HomePageHeader from "../components/HomePageHeader";
import { getAuthToken } from "../components/Auth";
import Map from "../components/Map";
import { useState, useEffect, useContext } from "react";
import { LocationContext } from "../context/LocationContext";
import { Await, useLoaderData } from "react-router-dom";
import { Suspense } from "react";
import BackdropLoader from "../utils/BackdropLoader";
import RestaurantCard from "../components/RestaurantCard";
import { redirect } from "react-router-dom";
import { Pagination } from "@mui/material";
import { HeatmapContext } from "../context/HeatmapContext";

export default function HomePage() {
  const { setLocation } = useContext(LocationContext);
  const { setDatetime } = useContext(HeatmapContext);
  const { data } = useLoaderData();

  const [page, setPage] = useState(1);

  useEffect(() => {
    const stored = localStorage.getItem("location");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.latitude && parsed.longitude) {
          setLocation({
            latitude: parsed.latitude,
            longitude: parsed.longitude,
          });
        }
      } catch (err) {
        console.error("Invalid location in localStorage", err);
      }
    }

    const now = new Date();
    now.setMinutes(0, 0, 0);

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hour = String(now.getHours()).padStart(2, "0");

    const localFormatted = `${year}-${month}-${day}T${hour}:00:00.000Z`;
    setDatetime(localFormatted);
  }, [setLocation, setDatetime]);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  useEffect(() => {
    const stored = localStorage.getItem("location");

    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.latitude && parsed.longitude) {
          setLocation({
            latitude: parsed.latitude,
            longitude: parsed.longitude,
          });
        }
      } catch (err) {
        console.error("Invalid location in localStorage", err);
      }
    }
  }, [setLocation]);

  return (
    <Suspense fallback={<BackdropLoader />}>
      <Await resolve={data}>
        {(restaurants) => {
          const itemsPerPage = 3;
          const paginatedItems = restaurants.slice(
            (page - 1) * itemsPerPage,
            page * itemsPerPage,
          );

          return (
            <>
              <HomePageHeader />
              <div className="mb-30 grid w-full auto-rows-min grid-cols-1 gap-4 lg:grid-cols-5">
                <div className="col-span-1 row-span-3 p-2 lg:col-span-3 lg:row-span-4">
                  <p className="m-5 text-2xl font-[700]">
                    Top Restaurants for You
                  </p>
                  <div className="m-5 grid grid-cols-1 items-center gap-5 sm:grid-cols-2 md:grid-cols-3">
                    {Array.isArray(restaurants) && paginatedItems.length > 0 ? (
                      paginatedItems.map((item) => (
                        <RestaurantCard key={item.restaurant_id} data={item} />
                      ))
                    ) : (
                      <p className="col-span-full text-gray-500">
                        No recommendations found.
                      </p>
                    )}
                  </div>

                  {restaurants.length > itemsPerPage && (
                    <div className="mt-6 flex justify-center">
                      <Pagination
                        count={Math.ceil(restaurants.length / itemsPerPage)}
                        page={page}
                        onChange={handlePageChange}
                        sx={{
                          "& .Mui-selected": {
                            backgroundColor: "#636AE8",
                            color: "#fff",
                            "&:hover": {
                              backgroundColor: "#5a61d1",
                            },
                          },
                          "& .MuiPaginationItem-root": {
                            borderRadius: "8px",
                          },
                        }}
                      />
                    </div>
                  )}
                </div>
                <div className="col-span-1 row-span-2 m-5 h-[600px] lg:col-span-2 lg:row-span-4">
                  <Map />
                </div>
              </div>
            </>
          );
        }}
      </Await>
    </Suspense>
  );
}

export function loader() {
  const token = getAuthToken();
  if (!token) return redirect("/");

  return {
    data: fetch(`${import.meta.env.VITE_API_URL}/restaurants/top-rated`, {
      headers: { "Content-Type": "application/json" },
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Response("Failed to restaurants", {
            status: response.status,
          });
        }
        return response.json();
      })
      .then((result) => result.restaurants),
  };
}
