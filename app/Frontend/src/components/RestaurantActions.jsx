import { BarChart, Heart } from "lucide-react";
import { useContext, useState } from "react";
import { RestaurantContext } from "./../context/RestaurantContext";
import { useNavigate } from "react-router-dom";
import BackdropLoader from "../utils/BackdropLoader";
import toast from "react-hot-toast";
import { getOrCreateSession } from "../utils/Session";

export default function RestaurantActions({ data }) {
  const { addRestaurant } = useContext(RestaurantContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleCompareClick = async () => {
    addRestaurant(data);
    setLoading(true);

    try {
      const userId = localStorage.getItem("user");

      // 🔥 Use the shared helper
      const sessionId = await getOrCreateSession(userId);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/comparison/session/${sessionId}/add_restaurant`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            restaurant_id: data.restaurant_id,
          }),
        },
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Failed to add to comparison.");
      }

      toast.success("Restaurant added to comparison!");
      navigate("/compare"); // ✅ Move this inside success block
    } catch (error) {
      console.error("Compare add error:", error);
      toast.error(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-gray-200 p-5 md:h-fit lg:h-full">
      <h1 className="mb-8 text-xl font-[500]">Actions</h1>
      <button
        onClick={handleCompareClick}
        className="mb-4 flex w-full cursor-pointer items-center justify-center gap-3 rounded-xl border border-gray-200 p-2 font-[500] transition-colors duration-200 ease-in hover:bg-indigo-500 hover:text-white"
      >
        <BarChart className="size-4" /> Compare
      </button>
      {loading && <BackdropLoader />}
    </div>
  );
}
