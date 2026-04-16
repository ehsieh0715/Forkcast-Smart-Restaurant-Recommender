import { redirect } from "react-router-dom";

export function loader() {
  return getAuthToken();
}

export function getAuthToken() {
  return localStorage.getItem("token");
}

export function getUserLocation() {
  return localStorage.getItem("location");
}

export function checkAuth({ request }) {
  const token = getAuthToken();
  const location = getUserLocation();

  if (!token) {
    return redirect("/");
  }

  const url = new URL(request.url);
  const pathname = url.pathname;

  const requiresLocation = ["/home", "/solo", "/group", "/compare"];

  if (!location && requiresLocation.includes(pathname)) {
    return redirect("/onboarding");
  }

  return null;
}

export function checkNoAuth() {
  const token = getAuthToken();

  if (token) {
    return redirect("/home");
  }
}
