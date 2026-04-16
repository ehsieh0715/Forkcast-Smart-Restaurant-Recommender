import { Outlet } from "react-router-dom";
import Navbar from "./../components/Navbar";
import Footer from "../components/Footer";
import ScrollToTop from "./../utils/ScrollToTop";

export default function NavbarRootPage() {
  return (
    <div className="flex min-h-screen flex-col justify-between">
      <ScrollToTop />
      <Navbar />
      <div className="flex-grow">
        <Outlet />
      </div>
      <Footer />
    </div>
  );
}
