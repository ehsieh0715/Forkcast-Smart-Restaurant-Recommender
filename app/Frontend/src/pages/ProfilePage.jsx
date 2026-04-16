import { useLoaderData, Await, redirect, useNavigate } from "react-router-dom";
import { Suspense } from "react";
import { getAuthToken } from "../components/Auth";
import BackdropLoader from "../utils/BackdropLoader";
import ProfileContent from "../components/ProfileContent";

export default function ProfilePage() {
  const { user } = useLoaderData();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <Suspense fallback={<BackdropLoader />}>
      <Await resolve={user}>
        {(user) => <ProfileContent user={user} onLogout={handleLogout} />}
      </Await>
    </Suspense>
  );
}

export async function loader() {
  const token = getAuthToken();
  if (!token) return redirect("/login");

  return {
    user: fetch(`${import.meta.env.VITE_API_URL}/authentication/profile`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }).then((response) => {
      if (!response.ok) {
        throw new Response("Failed to load profile", {
          status: response.status,
        });
      }
      return response.json();
    }),
  };
}
