import { useState, useEffect, useContext } from "react";
import SidebarFilters from "../components/SidebarFilters";
import Modal from "../components/Modal";
import { useMediaQuery } from "../hooks/useMediaQuery";
import RestaurantCard from "../components/RestaurantCard";
import { SlidersHorizontal, Utensils } from "lucide-react";
import Map from "../components/Map";
import { Pagination } from "@mui/material";
import { SoloRecommendationContext } from "./../context/SoloRecommendationContext";
import { LocationContext } from "../context/LocationContext";

export default function SoloPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  useContext(LocationContext);
  const { recommendations } = useContext(SoloRecommendationContext);

  const isLargeScreen = useMediaQuery("(min-width: 1024px)");

  const itemsPerPage = 4; // Adjust per your grid

  const [page, setPage] = useState(1);

  const paginatedItems = recommendations.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage,
  );

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleFilterClick = () => {
    setIsModalOpen(!isModalOpen);
  };

  useEffect(() => {
    setIsModalOpen(false);
  }, [isLargeScreen]);

  useEffect(() => {
    if (!isLargeScreen && isModalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }

    return () => {
      document.body.style.overflow = "auto"; // cleanup
    };
  }, [isModalOpen, isLargeScreen]);

  return (
    <>
      <div className="flex">
        <div className="m-5 hidden h-fit w-[100%] max-w-[350px] rounded-2xl border-1 border-gray-200 p-5 lg:block">
          <SidebarFilters />
        </div>

        <Modal open={isModalOpen} onClose={handleFilterClick}>
          <SidebarFilters onClose={handleFilterClick} />
        </Modal>

        <div className="m-5 grid w-full auto-rows-min gap-3">
          <div className="h-150">
            <Map />
          </div>

          <div className="flex items-center justify-between gap-20">
            <p className="my-2 text-sm font-[600] text-[#E8618C]">
              Recommendations are based on your preferences and real-time
              busyness.
            </p>

            <SlidersHorizontal
              onClick={handleFilterClick}
              className="cursor-pointer max-sm:size-10 lg:hidden"
            />
          </div>
          {recommendations.length > 0 && (
            <>
              <div
                className={`my-5 grid grid-cols-1 gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 max-[1299px]:lg:grid-cols-3`}
              >
                {paginatedItems.map((item) => (
                  <RestaurantCard key={item.restaurant_id} data={item} />
                ))}
              </div>

              <div className="mt-6 flex justify-center">
                <Pagination
                  count={Math.ceil(recommendations.length / itemsPerPage)}
                  page={page}
                  onChange={handlePageChange}
                  sx={{
                    "& .MuiPaginationItem-root": {
                      borderRadius: "8px", // Optional: make buttons rounded
                    },
                    "& .Mui-selected": {
                      backgroundColor: "#636AE8",
                      color: "#fff",
                      "&:hover": {
                        backgroundColor: "#5a61d1",
                      },
                    },
                  }}
                />
              </div>
            </>
          )}

          {recommendations.length == 0 && (
            <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-gray-200 py-10 text-center">
              <Utensils className="h-10 w-10 text-[#636AE8]" />
              <p className="max-w-md font-semibold text-gray-800 lg:text-lg">
                Choose your preference and get your recommendation!
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
