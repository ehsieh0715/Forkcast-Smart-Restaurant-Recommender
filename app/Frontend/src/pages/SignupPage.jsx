import { Form, Link, useNavigation } from "react-router-dom";
import BackdropLoader from "../utils/BackdropLoader";
import LoginGoogle from "../components/LoginGoogle";
import toast from "react-hot-toast";
import Map from "./../components/Map";
import { useContext, useEffect } from "react";
import { LocationContext } from "../context/LocationContext";
import { redirect } from "react-router-dom";

export default function SignupPage() {
  const navigation = useNavigation();
  const { location, setLocation } = useContext(LocationContext);

  useEffect(() => {
    const handleLocation = async () => {
      try {
        const position = await new Promise((resolve, reject) =>
          navigator.geolocation.getCurrentPosition(resolve, reject),
        );

        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      } catch (error) {
        console.log(error);
      }
    };

    handleLocation();
  }, []);

  return (
    <main className="grid w-full grid-cols-1 lg:h-screen lg:grid-cols-2">
      {/* Left - Signup Form (2/3) */}
      <div className="flex items-center justify-center">
        <div className="flex w-full max-w-120 flex-col gap-4 p-10 sm:max-w-175">
          <h1 className="text-center text-4xl font-bold">Register</h1>

          <div className="mx-auto mb-5">
            <LoginGoogle />
          </div>

          <div className="mb-5 flex items-center justify-between gap-2">
            <hr className="flex-1" />
            <span className="text-sm text-gray-500">OR</span>
            <hr className="flex-1" />
          </div>

          <Form method="post" action="password">
            <div className="mb-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-semibold tracking-[2px]"
                >
                  USERNAME
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label
                  htmlFor="fullname"
                  className="block text-sm font-semibold tracking-[2px]"
                >
                  FULL NAME
                </label>
                <input
                  type="text"
                  id="fullname"
                  name="fullname"
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-semibold tracking-[2px]"
                >
                  EMAIL
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-semibold tracking-[2px]"
                >
                  PASSWORD
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2"
                />
              </div>
            </div>
            {location?.latitude && location?.longitude && (
              <input
                type="hidden"
                name="location"
                required
                value={`${location.latitude},${location.longitude}`}
              />
            )}

            <button
              type="submit"
              className="m-auto block w-2/3 cursor-pointer rounded-full bg-[#636AE8] px-[25px] py-[12px] text-sm font-[700] text-white shadow-xl hover:bg-[rgba(81,120,255,255)]"
            >
              Submit
            </button>
          </Form>

          <p className="mt-4 text-center text-sm">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-semibold text-[#5167F6] hover:underline"
            >
              Login
            </Link>
          </p>
        </div>
      </div>

      {/* Right - Map (1/3) */}
      <div className="row-start-1 h-100 rounded-full max-md:m-5 lg:col-start-2 lg:h-full">
        <Map mode="locate" />
      </div>

      {navigation.state !== "idle" && <BackdropLoader />}
    </main>
  );
}

export async function action({ request }) {
  const formData = await request.formData();

  const locationString = formData.get("location");

  if (!locationString) {
    toast.error("Choose a location");
    return null;
  }

  const [lat, lng] = locationString.split(",").map(Number);

  const authdata = {
    email: formData.get("email"),
    username: formData.get("username"),
    name: formData.get("fullname"),
    password: formData.get("password"),
    latitude: lat,
    longitude: lng,
  };

  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/authentication/signup`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(authdata),
      },
    );

    const responseData = await response.json();

    if (response.status === 201) {
      toast.success("Signup successful!");
      return redirect("/login");
    } else {
      toast.error(responseData.error || "Signup failed.");
      return null;
    }
  } catch (error) {
    console.error("Signup error:", error);
    toast.error("Something went wrong. Please try again.");
    return null;
  }
}
