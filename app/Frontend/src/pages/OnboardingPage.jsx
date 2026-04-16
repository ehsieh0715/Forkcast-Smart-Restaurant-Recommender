import { useNavigate } from "react-router-dom";
import Map from "../components/Map";
import { useContext } from "react";
import { LocationContext } from "../context/LocationContext";

export default function OnboardingPage() {
  const { location } = useContext(LocationContext);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!location?.latitude || !location?.longitude) return;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/authentication/profile`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            latitude: location.latitude.toFixed(4),
            longitude: location.longitude.toFixed(4),
          }),
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage;
        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.message || JSON.stringify(errorJson);
        } catch {
          errorMessage = errorText || "Unknown error";
        }

        throw new Error(`Failed to update profile: ${errorMessage}`);
      }

      const data = await response.json();

      localStorage.setItem("location", JSON.stringify(location));
      navigate("/home");

      return data;
    } catch (error) {
      console.error("Error updating profile location:", error);
      // You can optionally toast error here
    }
  };

  return (
    <div className="flex h-full items-center justify-center bg-gray-100 px-4 py-6">
      <div className="w-full max-w-4xl rounded-2xl bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-center text-3xl font-bold">
          Choose Your Location
        </h1>

        <div className="mb-4 h-[400px] w-full overflow-hidden rounded-xl border border-gray-300">
          <Map mode="locate" />
        </div>

        {location?.latitude && location?.longitude && (
          <p className="mb-2 text-center text-sm text-gray-600">
            Selected: ({location.latitude.toFixed(4)},{" "}
            {location.longitude.toFixed(4)})
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={!location?.latitude || !location?.longitude}
          className={`mt-4 w-full rounded-md px-4 py-2 text-white transition ${
            location?.latitude && location?.longitude
              ? "bg-indigo-600 hover:bg-indigo-700"
              : "cursor-not-allowed bg-gray-400"
          }`}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
