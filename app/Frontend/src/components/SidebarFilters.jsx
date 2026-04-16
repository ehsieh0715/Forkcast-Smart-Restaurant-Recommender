import { GroupRecommendationContext } from "../context/GroupRecommendationContext";
import { useContext, useEffect, useState } from "react";
import { LocationContext } from "../context/LocationContext";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import BackdropLoader from "./../utils/BackdropLoader";
import toast from "react-hot-toast";
import Slider from "@mui/material/Slider";
import { Users } from "lucide-react";
import { SoloRecommendationContext } from "../context/SoloRecommendationContext";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { HeatmapContext } from "../context/HeatmapContext";

export default function SidebarFilters({
  onClose,
  mode = "solo",
  group_Id = null,
  onPreferencesUpdated,
}) {
  const { location } = useContext(LocationContext);
  const { handleRecommendations } = useContext(SoloRecommendationContext);
  const { handleGroupRecommendations } = useContext(GroupRecommendationContext);
  const { setDatetime } = useContext(HeatmapContext);

  const getRoundedLocalDateTimeString = () => {
    const now = new Date();
    now.setMinutes(0, 0, 0);
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hour = String(now.getHours()).padStart(2, "0");
    return `${year}-${month}-${day}T${hour}:00`;
  };

  const [filterData, setFilterData] = useState(null);
  const [cuisinePreferences, setCuisinePreferences] = useState([]);
  const [priceLevel, setPriceLevel] = useState("Cheap");
  const [rating, setRating] = useState(3);
  const [reviewCount, setReviewCount] = useState("");
  const [distancePreference, setDistancePreference] = useState("");
  const [desiredDatetime, setDesiredDatetime] = useState(
    getRoundedLocalDateTimeString(),
  );
  const [busynessPreference, setBusynessPreference] = useState(3);
  const [loading, setLoading] = useState(false);

  const crowdIcons = {
    1: <Users className="text-green-500" size={16} />,
    2: <Users className="text-lime-500" size={16} />,
    3: <Users className="text-yellow-500" size={16} />,
    4: <Users className="text-orange-500" size={16} />,
    5: <Users className="text-red-600" size={16} />,
  };

  useEffect(() => {
    const getFilters = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/filters/options`,
        );
        const data = await response.json();
        setFilterData(data);
      } catch (err) {
        toast.error("Failed to fetch filters");
        console.error("Error fetching filters:", err);
      } finally {
        setLoading(false);
      }
    };
    getFilters();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (cuisinePreferences.length === 0) {
      toast.error("Please select at least one cuisine.");
      return;
    }

    const resolvedLocation =
      location?.latitude && location?.longitude
        ? { lat: location.latitude, lon: location.longitude }
        : { lat: 40.7831, lon: -73.9712 };

    const desiredISOTime = `${desiredDatetime}:00.000Z`;
    setDatetime(desiredISOTime);

    let payload;

    if (mode === "solo") {
      payload = {
        location: resolvedLocation,
        cuisine_preferences: cuisinePreferences,
        price_level: priceLevel,
        desired_datetime: desiredISOTime,
      };

      if (rating) payload.rating = rating;
      if (reviewCount) payload.review_count = parseInt(reviewCount);
      if (busynessPreference)
        payload.busyness_preference = parseInt(busynessPreference);
    }

    if (mode === "group") {
      const priceMap = { Cheap: 1, Medium: 2, Expensive: 3 };

      const preferences = {
        cuisine_preferences: cuisinePreferences,
        distance_preference: distancePreference
          ? parseInt(distancePreference)
          : undefined,
        busyness_preference: busynessPreference,
        minimum_rating: rating,
        price_level: priceMap[priceLevel],
      };

      Object.keys(preferences).forEach(
        (key) => preferences[key] === undefined && delete preferences[key],
      );

      payload = {
        user_id: localStorage.getItem("user") ?? undefined,
        preferences,
      };
    }

    setLoading(true);

    try {
      if (mode === "solo") {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/personal/recommendation`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          },
        );

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();
        handleRecommendations(data.recommendations);
        toast.success("Fetched solo recommendations");
      }

      if (mode === "group") {
        const postResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/group/session/${group_Id}/submit_preferences`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          },
        );

        if (!postResponse.ok) throw new Error("Failed to submit preferences");

        const resultResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/group/session/${group_Id}/results?latitude=${resolvedLocation.lat}&longitude=${resolvedLocation.lon}&desired_datetime=${desiredISOTime}`,
        );

        if (!resultResponse.ok)
          throw new Error("Failed to get recommendations");

        const resultData = await resultResponse.json();
        handleGroupRecommendations(resultData.recommendations);
        onPreferencesUpdated();

        toast.success("Fetched group recommendations");
      }
    } catch (error) {
      console.error(error);
      toast.error("Failed to fetch. Please try again.");
    } finally {
      if (onClose) onClose();
      setLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <p className="text-2xl font-[700]">Refine your taste</p>
        <p className="mb-5 text-[#8C8D8B]">Customize your preferences</p>

        <Autocomplete
          multiple
          options={filterData?.filters?.cuisine_types || []}
          getOptionLabel={(option) => option}
          value={cuisinePreferences}
          onChange={(e, value) => setCuisinePreferences(value)}
          renderInput={(params) => (
            <TextField {...params} label="Cuisine Type" size="small" />
          )}
          sx={{ marginBottom: 3 }}
        />

        <div className="mb-4">
          <p className="mb-2 font-[500] text-[#8C8D8B]">Price Level</p>
          {["Cheap", "Medium", "Expensive"].map((level) => (
            <label key={level} className="mr-4">
              <input
                type="radio"
                name="price"
                value={level}
                required
                checked={priceLevel === level}
                onChange={() => setPriceLevel(level)}
                className="mr-2"
              />
              {level}
            </label>
          ))}
        </div>

        {mode === "group" && (
          <div className="mb-4">
            <label className="mb-1 block font-[500] text-[#8C8D8B]">
              Max Distance (Meters)
            </label>
            <input
              type="number"
              min="0"
              value={distancePreference}
              required
              onChange={(e) => setDistancePreference(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        )}

        <div className="mb-6">
          <label
            htmlFor="rating-slider"
            className="mb-2 block font-[500] text-[#8C8D8B]"
          >
            Star Rating
          </label>

          <Slider
            id="rating-slider"
            value={rating}
            onChange={(e, newValue) => setRating(newValue)}
            step={1}
            min={1}
            max={5}
            marks={[
              { value: 1 },
              { value: 2 },
              { value: 3 },
              { value: 4 },
              { value: 5 },
            ]}
            track="inverted"
            valueLabelDisplay="auto"
            sx={{
              color: "#636AE8",
            }}
          />

          <div className="mt-2 flex justify-between text-sm text-black">
            {[1, 2, 3, 4, 5].map((val) => (
              <span key={val}>{val}</span>
            ))}
          </div>
        </div>

        {mode === "solo" && (
          <div className="mb-4">
            <label className="mb-1 block font-[500] text-[#8C8D8B]">
              Minimum Review Count
            </label>
            <input
              type="number"
              min="0"
              value={reviewCount}
              onChange={(e) => setReviewCount(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        )}

        <div className="mb-4">
          <label className="mb-1 block font-[500] text-[#8C8D8B]">
            Desired Date & Time
          </label>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DateTimePicker
              views={["year", "month", "day", "hours"]}
              value={new Date(desiredDatetime)}
              onChange={(newValue) => {
                if (newValue) {
                  const rounded = new Date(newValue);
                  rounded.setMinutes(0, 0, 0);
                  const year = rounded.getFullYear();
                  const month = String(rounded.getMonth() + 1).padStart(2, "0");
                  const day = String(rounded.getDate()).padStart(2, "0");
                  const hour = String(rounded.getHours()).padStart(2, "0");
                  setDesiredDatetime(`${year}-${month}-${day}T${hour}:00`);
                }
              }}
              onAccept={(finalValue) => {
                if (finalValue) {
                  const rounded = new Date(finalValue);
                  rounded.setMinutes(0, 0, 0);

                  const year = rounded.getFullYear();
                  const month = String(rounded.getMonth() + 1).padStart(2, "0");
                  const day = String(rounded.getDate()).padStart(2, "0");
                  const hour = String(rounded.getHours()).padStart(2, "0");
                  const minute = "00";

                  const localFormatted = `${year}-${month}-${day}T${hour}:${minute}:00.000Z`;
                  setDatetime(localFormatted);
                }
              }}
              minutesStep={60}
              ampm={true}
              renderInput={(params) => (
                <TextField
                  {...params}
                  required
                  size="small"
                  fullWidth
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: "0.375rem",
                      backgroundColor: "#fff",
                      borderColor: "#a5b4fc",
                    },
                    "& .MuiOutlinedInput-notchedOutline": {
                      borderColor: "#a5b4fc",
                    },
                    "&:hover .MuiOutlinedInput-notchedOutline": {
                      borderColor: "#6366f1",
                    },
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "#6366f1",
                      borderWidth: "2px",
                    },
                    "& .MuiInputBase-input": {
                      fontSize: "0.875rem",
                      padding: "10px 12px",
                    },
                  }}
                />
              )}
            />
          </LocalizationProvider>
        </div>

        <div className="mb-6">
          <p className="mb-2 font-[500] text-[#0d110a]">
            Preferred Crowd Level
          </p>
          <Slider
            value={busynessPreference}
            onChange={(e, newValue) => setBusynessPreference(newValue)}
            step={1}
            marks
            min={1}
            max={5}
            valueLabelDisplay="auto"
            sx={{
              color: "#636AE8",
              "& .MuiSlider-thumb": { backgroundColor: "#636AE8" },
              "& .MuiSlider-track": { backgroundColor: "#636AE8" },
              "& .MuiSlider-rail": { backgroundColor: "#E0E0E0" },
            }}
          />
          <div className="mt-3 flex justify-between text-xs">
            {[1, 2, 3, 4, 5].map((level) => (
              <div key={level} className="flex flex-col items-center gap-1">
                <span className="text-sm font-medium">{level}</span>
                {crowdIcons[level]}
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col items-center gap-4">
          <button
            type="submit"
            className="w-3/4 rounded-lg bg-[#636AE8] px-4 py-2 text-white hover:bg-indigo-600"
          >
            Get Recommendations
          </button>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="w-3/4 rounded-lg border border-gray-300 px-4 py-2 text-[#636AE8] hover:bg-gray-100"
          >
            Clear Preferences
          </button>
        </div>
      </form>

      {loading && <BackdropLoader />}
    </>
  );
}
