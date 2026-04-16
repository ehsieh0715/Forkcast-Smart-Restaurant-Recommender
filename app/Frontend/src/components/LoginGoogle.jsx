import { GoogleLogin } from "@react-oauth/google";
import { redirect, useSubmit } from "react-router-dom";
import toast from "react-hot-toast";
import { useContext } from "react";
import { LocationContext } from "../context/LocationContext";

export default function LoginGoogle() {
  const submit = useSubmit();
  const { location } = useContext(LocationContext);

  const handleGoogleLogin = (credentialResponse) => {
    if (!credentialResponse?.credential) {
      toast.error("Missing credentials");
      return;
    }

    const geo = JSON.stringify(location);

    submit(
      {
        token: credentialResponse.credential,
        geo,
      },
      { method: "post", action: "/login/google" },
    );
  };

  return (
    <GoogleLogin
      onSuccess={handleGoogleLogin}
      onError={() => {
        toast.error("Login failed");
      }}
      auto_select={false}
    />
  );
}

export async function action({ request }) {
  const data = await request.formData();

  const credential = data.get("token");
  const rawGeo = data.get("geo");

  let geoLocation = null;

  try {
    if (rawGeo) {
      const parsed = JSON.parse(rawGeo);
      if (parsed.latitude && parsed.longitude) {
        geoLocation = {
          latitude: parsed.latitude,
          longitude: parsed.longitude,
        };
      }
    }
  } catch (err) {
    console.error("Invalid geo format", rawGeo, err);
  }

  const authdata = {
    credential,
    ...(geoLocation && { location: geoLocation }),
  };

  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/authentication/google`,
    {
      method: "POST",
      body: JSON.stringify(authdata),
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  const responseData = await response.json();

  if (response.status === 200) {
    const { access_token, user } = responseData;

    localStorage.setItem("token", access_token);
    localStorage.setItem("user", user.user_id);
    localStorage.setItem("username", user.name);

    const finalLocation =
      user.location?.latitude && user.location?.longitude
        ? user.location
        : geoLocation;

    if (finalLocation) {
      localStorage.setItem("location", JSON.stringify(finalLocation));
      return redirect("/home");
    } else {
      return redirect("/onboarding");
    }
  } else {
    toast.error(responseData.error || "Login failed");
  }
}
