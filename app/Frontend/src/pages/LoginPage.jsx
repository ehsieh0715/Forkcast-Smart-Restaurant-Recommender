import { Form, Link, redirect, useNavigation } from "react-router-dom";
import "./../App.css";
import toast from "react-hot-toast";
import BackdropLoader from "./../utils/BackdropLoader";
import LoginGoogle from "../components/LoginGoogle";
import { useContext, useEffect } from "react";
import { LocationContext } from "../context/LocationContext";

export default function LoginPage() {
  const loading = useNavigation();
  const { setLocation } = useContext(LocationContext);

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
    <main className="flex h-screen w-full flex-col lg:flex-row">
      {/* Left - Image (1/3) */}
      <div className="h-70 md:h-80 lg:h-full lg:w-1/3">
        <img
          src="loginpage.jpg"
          className="h-full w-full object-cover"
          alt="login"
        />
      </div>

      {/* Right - Form (2/3) */}
      <div className="flex w-full items-center justify-center bg-[url(/form-graphic.svg)] bg-contain bg-right-bottom bg-no-repeat lg:w-2/3">
        <div className="w-full max-w-150 p-10">
          <h1 className="my-5 text-center text-[48px] font-[700]">Sign In</h1>

          <div className="mx-auto mb-10 w-fit">
            <LoginGoogle />
          </div>

          <div className="mb-5 flex items-center justify-between gap-2">
            <hr className="flex-1" />
            <span className="text-sm text-gray-500">OR</span>
            <hr className="flex-1" />
          </div>

          <Form
            method="post"
            className="flex flex-col gap-[16px]"
            action="password"
          >
            <div>
              <label
                htmlFor="username"
                className="block text-[14px] font-[600] tracking-[2px]"
              >
                USERNAME
              </label>
              <input
                type="text"
                id="username"
                name="username"
                required
                className="mt-[8px] w-full rounded-[16px] border-2 border-gray-200 px-[12px] py-[12px]"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-[14px] font-[600] tracking-[2px]"
              >
                PASSWORD
              </label>
              <input
                type="password"
                id="password"
                name="password"
                required
                className="mt-[8px] w-full rounded-[16px] border-2 border-gray-200 px-[12px] py-[12px]"
              />
            </div>

            <p className="text-center text-[14px]">
              Forgot Password?{" "}
              <Link
                to="/signup"
                className="font-[600] text-[rgba(81,103,246,255)] hover:underline"
              >
                Reset
              </Link>
            </p>

            <button
              type="submit"
              className="m-auto block w-2/3 cursor-pointer rounded-full bg-[#636AE8] px-[25px] py-[12px] text-xs font-[700] text-white shadow-xl hover:bg-[rgba(81,120,255,255)] md:text-sm"
            >
              Submit
            </button>
          </Form>

          <p className="mt-4 text-center text-[14px]">
            Don't have an account yet?{" "}
            <Link
              to="/signup"
              className="font-[600] text-[rgba(81,103,246,255)] hover:underline"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>

      {loading.state !== "idle" && <BackdropLoader />}
    </main>
  );
}

export async function action({ request }) {
  const data = await request.formData();

  const authdata = {
    username: data.get("username"),
    password: data.get("password"),
  };

  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/authentication/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: authdata.username,
        password: authdata.password,
      }),
    },
  );

  const responseData = await response.json();

  if (response.status == 200) {
    localStorage.setItem("token", responseData.access_token);
    localStorage.setItem("user", responseData["user"]["user_id"]);
    localStorage.setItem("username", responseData["user"]["name"]);
    localStorage.setItem(
      "location",
      JSON.stringify(responseData["user"]["location"]),
    );
    return redirect("/home");
  } else {
    toast.error("Username or password was incorrect!");
  }
}
