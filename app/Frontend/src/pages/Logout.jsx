import { redirect } from "react-router-dom";

export async function action() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("username");
  localStorage.removeItem("sessionId");
  localStorage.removeItem("location");
  return redirect("/");
}
