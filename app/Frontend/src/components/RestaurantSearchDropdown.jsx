import { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { Autocomplete, TextField } from "@mui/material";
import toast from "react-hot-toast";
import BackdropLoader from "../utils/BackdropLoader";
import { RestaurantContext } from "../context/RestaurantContext";
import { HeatmapContext } from "./../context/HeatmapContext";

export default function RestaurantSearchDropdown({ mode = "search" }) {
  const [loading, setLoading] = useState(false);
  const { datetime } = useContext(HeatmapContext);
  const navigate = useNavigate();
  const { addRestaurant, allRestaurants, setAllRestaurants } =
    useContext(RestaurantContext);

  useEffect(() => {
    const fetchRestaurants = async () => {
      // Don't re-fetch if already cached
      if (allRestaurants.length > 0) return;

      setLoading(true);
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/restaurants`);
        const data = await res.json();
        setAllRestaurants(data.restaurants);
      } catch (err) {
        toast.error("Failed to fetch restaurants");
        console.error("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchRestaurants();
  }, [allRestaurants, setAllRestaurants]);

  const handleSelect = async (event, value) => {
    if (!value) return;

    if (mode === "search") {
      navigate(`/restaurant/${value.restaurant_id}`);
    } else if (mode === "compare") {
      setLoading(true);
      try {
        const sessionId = localStorage.getItem("sessionId");
        const userId = localStorage.getItem("user");

        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/comparison/session/${sessionId}/add_restaurant`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              user_id: userId,
              restaurant_id: value.restaurant_id,
            }),
          },
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.message || "Failed to add to comparison.");
        }

        let url = `${import.meta.env.VITE_API_URL}/restaurants/${value.restaurant_id}`;

        if (datetime != null) {
          url += `?requested_time=${datetime}`;
        }

        const res = await fetch(url);
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.message || "Failed to fetch restaurant.");
        }

        const fetchedRestaurantData = await res.json();
        addRestaurant(fetchedRestaurantData);

        toast.success("Restaurant added to comparison!");
      } catch (error) {
        console.error("Compare add error:", error);
        toast.error(`Error: ${error.message}`);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <>
      <Autocomplete
        options={allRestaurants}
        getOptionLabel={(option) => option.full_name}
        onChange={handleSelect}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Search restaurants..."
            variant="outlined"
            size="small"
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: "12px",
                backgroundColor: "#fff",
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                transition: "all 0.2s ease",
                "&:hover": {
                  boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
                },
                "&.Mui-focused": {
                  borderColor: "#636AE8",
                  boxShadow: "0 0 0 2px rgba(99, 106, 232, 0.2)",
                },
              },
              "& .MuiInputLabel-root": {
                fontWeight: 500,
              },
            }}
          />
        )}
        sx={{
          width: "100%",
          maxWidth: 300,
          "& .MuiAutocomplete-popupIndicator": {
            color: "#636AE8",
          },
          "& .MuiAutocomplete-option": {
            borderRadius: "8px",
            margin: "2px 4px",
            padding: "6px 12px",
            fontSize: "0.9rem",
            "&[aria-selected='true']": {
              backgroundColor: "#636AE810",
              color: "#636AE8",
            },
            "&:hover": {
              backgroundColor: "#f1f1ff",
            },
          },
        }}
        isOptionEqualToValue={(option, value) =>
          option.place_id === value.place_id
        }
      />

      {loading && <BackdropLoader />}
    </>
  );
}
