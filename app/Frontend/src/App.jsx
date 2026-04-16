import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import LoginPage, { action as loginAction } from "./pages/LoginPage";
import { action as googleLoginAction } from "./components/LoginGoogle";
import ProfilePage, { loader as profileLoader } from "./pages/ProfilePage";
import SignupPage, { action as signupAction } from "./pages/SignupPage";
import LandingPage from "./pages/LandingPage";
import { GoogleOAuthProvider } from "@react-oauth/google";
import HomePage, { loader as homePageLoader } from "./pages/HomePage";
import RootPage from "./pages/RootPage";
import ErrorPage from "./pages/ErrorPage";
import GroupPage, { loader as groupPageLoader } from "./pages/GroupPage";
import SoloPage from "./pages/SoloPage";
import GroupRecommendationContextProvider from "./context/GroupRecommendationContext";
import ComparisonPage, {
  loader as comparisonPageLoader,
} from "./pages/ComparisonPage";
import { RestaurantProvider } from "./context/RestaurantContext";
import LocationContextProvider from "./context/LocationContext";
import RestaurantDetails, {
  loader as restaurantDetailsLoader,
} from "./pages/RestaurantDetails";
import { action as logoutAction } from "./pages/Logout";
import {
  loader as authLoader,
  checkAuth,
  checkNoAuth,
} from "./components/Auth";
import NavbarRootPage from "./pages/NavbarRootPage";
import { Toaster } from "react-hot-toast";
import SoloRecommendationContextProvider from "./context/SoloRecommendationContext";
import OnboardingPage from "./pages/OnboardingPage";
import HeatmapProvider from "./context/HeatmapContext";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootPage />,
    errorElement: <ErrorPage />,
    id: "root",
    loader: authLoader,
    children: [
      {
        path: "",
        element: <NavbarRootPage />,
        children: [
          { index: true, element: <LandingPage />, loader: checkNoAuth },
          { path: "home", element: <HomePage />, loader: homePageLoader },
          { path: "solo", element: <SoloPage />, loader: checkAuth },
          { path: "group", element: <GroupPage />, loader: groupPageLoader },
          {
            path: "onboarding",
            element: <OnboardingPage />,
            loader: checkAuth,
          },
          { path: "profile", element: <ProfilePage />, loader: profileLoader },
          {
            path: "restaurant/:datetime/:restaurantId",
            element: <RestaurantDetails />,
            loader: restaurantDetailsLoader,
          },
          {
            path: "compare",
            element: <ComparisonPage />,
            loader: comparisonPageLoader,
          },
        ],
      },
      {
        path: "login",
        element: <LoginPage />,
        loader: checkNoAuth,
        children: [
          {
            path: "google",
            action: googleLoginAction,
          },
          {
            path: "password",
            action: loginAction,
          },
        ],
      },
      {
        path: "signup",
        element: <SignupPage />,
        loader: checkNoAuth,
        children: [
          {
            path: "google",
            action: googleLoginAction,
          },
          {
            path: "password",
            action: signupAction,
          },
        ],
      },
      { path: "/logout", action: logoutAction },
    ],
  },
]);

const CLIENT_ID =
  "825269171399-nr6gltep04clm8b1saspkf8g0hp1v5kd.apps.googleusercontent.com";

function App() {
  return (
    <GoogleOAuthProvider clientId={CLIENT_ID}>
      <HeatmapProvider>
        <GroupRecommendationContextProvider>
          <SoloRecommendationContextProvider>
            <RestaurantProvider>
              <LocationContextProvider>
                <Toaster
                  position="top-center"
                  toastOptions={{
                    style: {
                      marginTop: "50px",
                      position: "relative",
                      zIndex: 100,
                    },
                  }}
                />
                <RouterProvider router={router}></RouterProvider>
              </LocationContextProvider>
            </RestaurantProvider>
          </SoloRecommendationContextProvider>
        </GroupRecommendationContextProvider>
      </HeatmapProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
