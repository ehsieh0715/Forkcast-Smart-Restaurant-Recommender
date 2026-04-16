import {
  Link,
  NavLink,
  useRouteLoaderData,
  Form,
  useNavigate,
  useSubmit,
} from "react-router-dom";
import { useState } from "react";
import {
  CircleUserRound,
  Search,
  MenuIcon,
  X,
  LogOut,
  User,
} from "lucide-react";
import { Menu, MenuItem } from "@mui/material";
import RestaurantSearchDropdown from "./RestaurantSearchDropdown";
import { useContext } from "react";
import { LocationContext } from "../context/LocationContext";

export default function PageNavbar() {
  const data = useRouteLoaderData("root");
  const [menuOpen, setMenuOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const username = localStorage.getItem("username");
  const submit = useSubmit();
  const { clearLocation } = useContext(LocationContext);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
    setMenuOpen(false);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    clearLocation();

    submit(null, { method: "post", action: "/logout" });
  };

  return (
    <nav className="bg-white">
      <div className="flex items-center justify-between px-4 py-4 md:px-[3%]">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <img src="/Forkcast.svg" className="w-30 md:w-35" alt="Logo" />
        </div>

        {/* Desktop Nav Links */}
        {data && (
          <div className="hidden w-[60%] items-center justify-center gap-6 font-[700] lg:flex">
            {[
              { to: "/home", label: "Home" },
              { to: "/solo", label: "Solo" },
              { to: "/group", label: "Group" },
              { to: "/compare", label: "Comparison" },
            ].map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `group relative inline-flex items-center justify-center rounded-xl px-4 py-2 transition-all duration-300 ease-in-out ${
                    isActive
                      ? "bg-[#636AE8]/10 text-[#636AE8] shadow-sm backdrop-blur-sm"
                      : "text-gray-700 hover:bg-gray-100/70 hover:text-[#636AE8] dark:text-gray-300 dark:hover:text-[#636AE8]"
                  }`
                }
              >
                <span className="relative z-10">{label}</span>
                <span className="absolute bottom-0 left-1/2 h-[2px] w-0 bg-[#636AE8] transition-all duration-300 ease-in-out group-hover:left-0 group-hover:w-full"></span>
              </NavLink>
            ))}
          </div>
        )}

        {/* Guest Buttons */}
        {!data && (
          <ul className="flex items-center gap-[8px]">
            <li>
              <Link
                to="/login"
                className="block cursor-pointer rounded-[48px] bg-transparent px-[15px] py-[4px] text-[12px] font-[700] shadow-xl hover:bg-[rgb(252,248,248)] md:px-[24px] md:py-[8px] md:text-sm"
              >
                Login
              </Link>
            </li>
            <li>
              <Link
                to="/signup"
                className="block cursor-pointer rounded-[48px] bg-[#636AE8] px-[15px] py-[4px] text-[12px] font-[700] text-white shadow-xl hover:bg-[rgba(81,120,255,255)] md:px-[24px] md:py-[8px] md:text-sm"
              >
                Signup
              </Link>
            </li>
          </ul>
        )}

        {/* Search + Menu + Profile */}
        {data && (
          <div className="flex items-center justify-center gap-3">
            <div className="w-40 md:w-64 lg:w-72">
              <RestaurantSearchDropdown />
            </div>

            {/* Hamburger for Mobile */}
            <button
              onClick={() => {
                setMenuOpen(!menuOpen);
                setAnchorEl(null);
              }}
              className="cursor-pointer text-gray-500 focus:outline-none lg:hidden"
            >
              {menuOpen ? (
                <X className="size-5 transition-colors duration-200 ease-in hover:text-indigo-400" />
              ) : (
                <MenuIcon className="size-5 transition-colors duration-200 ease-in hover:text-indigo-400" />
              )}
            </button>

            {/* MUI Profile Menu */}
            <button onClick={handleMenuOpen} className="cursor-pointer">
              <CircleUserRound className="size-5 text-gray-500 transition-colors duration-200 ease-in hover:text-indigo-400 lg:size-6" />
            </button>
            <Menu
              id="user-menu"
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              PaperProps={{
                elevation: 6,
                sx: {
                  mt: 1.5,
                  borderRadius: 3,
                  minWidth: 220,
                  paddingY: 1,
                  boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.08)",
                },
              }}
              transformOrigin={{ horizontal: "right", vertical: "top" }}
              anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
            >
              {/* User Info Header */}
              <div className="px-4 py-3">
                <p className="text-sm text-gray-500">Signed in as</p>
                <p className="truncate text-sm font-semibold text-gray-900">
                  {username || "Unknown User"}
                </p>
              </div>
              <hr className="mx-3 my-1 border-gray-200" />

              {/* Account */}
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  navigate("/profile");
                }}
                sx={{
                  fontSize: "0.875rem",
                  paddingY: "10px",
                  paddingX: "16px",
                  "&:hover": {
                    backgroundColor: "#f5f5f5",
                  },
                }}
              >
                <User className="mr-2 size-4 text-indigo-500" />
                Account
              </MenuItem>

              {/* Logout */}

              <MenuItem
                disableGutters
                sx={{
                  paddingY: 0,
                  paddingX: 0,
                }}
              >
                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex w-full cursor-pointer items-center px-4 py-2 text-sm hover:bg-red-50"
                >
                  <LogOut className="mr-2 size-4 text-red-500" />
                  Logout
                </button>
              </MenuItem>
            </Menu>
          </div>
        )}
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="animate-slideDownFade fixed inset-0 z-50 flex flex-col bg-white text-black lg:hidden">
          <div className="flex items-center justify-between border-b border-gray-200 p-4">
            <img src="/Forkcast.svg" alt="Logo" className="h-6 w-auto md:h-8" />
            <button
              onClick={() => setMenuOpen(false)}
              className="rounded border border-gray-300 p-1 transition hover:border-gray-500"
            >
              <X className="size-5 text-gray-700" />
            </button>
          </div>

          <div className="flex flex-col items-center gap-4 px-6 py-8 text-base font-[800]">
            {[
              { to: "/home", label: "Home" },
              { to: "/solo", label: "Solo" },
              { to: "/group", label: "Group" },
              { to: "/compare", label: "Comparison" },
            ].map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `w-full max-w-[300px] rounded-md px-4 py-2 text-center transition-all duration-200 ${
                    isActive
                      ? "bg-[#636AE8]/10 font-semibold text-[#636AE8]"
                      : "text-gray-700 hover:bg-gray-100 hover:text-[#636AE8]"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
