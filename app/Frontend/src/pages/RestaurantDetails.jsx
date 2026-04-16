import { useLoaderData, Await, useNavigate } from "react-router-dom";
import { Suspense } from "react";
import RestaurantDetailsHeader from "../components/RestaurantDetailsHeader";
import RestaurantDetailsContent from "../components/RestaurantDetailsContent";
import BackdropLoader from "../utils/BackdropLoader";
import { useParams } from "react-router-dom";
import { redirect } from "react-router-dom";
import { getAuthToken } from "../components/Auth";

export default function RestaurantDetails() {
  const { data } = useLoaderData();
  const navigate = useNavigate();
  const { restaurantId } = useParams();

  return (
    <Suspense fallback={<BackdropLoader />} key={restaurantId}>
      <Await resolve={data}>
        {(resolvedData) => (
          <main className="m-10">
            <button
              onClick={() => navigate(-1)}
              className="cursor-pointer rounded-md border-2 border-[#636AE8] bg-[#636AE8] px-10 py-2 text-xs font-[600] text-white transition duration-200 ease-in hover:bg-white hover:text-[#636AE8]"
            >
              Back
            </button>
            <RestaurantDetailsHeader data={resolvedData} />
            <RestaurantDetailsContent data={resolvedData} />
          </main>
        )}
      </Await>
    </Suspense>
  );
}

export async function loader({ params }) {
  const token = getAuthToken();
  if (!token) return redirect("/");

  const { restaurantId, datetime } = params;

  let url = `${import.meta.env.VITE_API_URL}/restaurants/${restaurantId}`;

  if (datetime != null) {
    url += `?requested_time=${datetime}`;
  }

  return {
    data: fetch(url).then((res) => {
      if (!res.ok) {
        throw new Response("Failed to load restaurant", {
          status: res.status,
        });
      }
      return res.json();
    }),
  };
}
