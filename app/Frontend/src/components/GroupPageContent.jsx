import SidebarFilters from "./../components/SidebarFilters";
import { useState, useEffect } from "react";
import { useMediaQuery } from "../hooks/useMediaQuery";
import Modal from "./Modal";
import { User, Users2, ArrowRight, Crown } from "lucide-react";
import Map from "./Map";
import { Pagination } from "@mui/material";
import PreferenceDisplay from "./PreferenceDisplay";
import { useContext } from "react";
import { GroupRecommendationContext } from "../context/GroupRecommendationContext";
import RestaurantCard from "./RestaurantCard";

export default function GroupPageContent({ group, setGroup }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);
  const [isPrefModalOpen, setIsPrefModalOpen] = useState(false);
  const isLargeScreen = useMediaQuery("(min-width: 1024px)");

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
      document.body.style.overflow = "auto";
    };
  }, [isModalOpen, isLargeScreen]);

  const { groupRecommendations } = useContext(GroupRecommendationContext);

  const [groupPage, setGroupPage] = useState(1);
  const groupItemsPerPage = 3;

  const paginatedGroupItems = groupRecommendations.slice(
    (groupPage - 1) * groupItemsPerPage,
    groupPage * groupItemsPerPage,
  );

  const handleGroupPageChange = (event, value) => {
    setGroupPage(value);
  };

  const fetchGroupMembers = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/group/session/${group.id}/members`,
        {
          headers: { "Content-Type": "application/json" },
        },
      );
      const data = await response.json();

      // Replace only members in the group object
      setSelectedMember(null); // optional: reset open modal user
      setGroup((prev) => ({
        ...prev,
        members: data.group.members,
      }));
    } catch (error) {
      console.error("Failed to refresh group members", error);
    }
  };

  return (
    <div className="m-10 flex flex-col gap-10 lg:flex-row">
      <div className="flex flex-col gap-6 lg:w-1/3">
        <div className="rounded-2xl border border-gray-200 p-7">
          <SidebarFilters
            mode="group"
            group_Id={group.id}
            onPreferencesUpdated={fetchGroupMembers}
          />
        </div>

        <Modal open={isModalOpen} onClose={handleFilterClick}>
          <SidebarFilters
            mode="group"
            group_Id={group.id}
            onPreferencesUpdated={fetchGroupMembers}
          />
        </Modal>

        <Modal open={isPrefModalOpen} onClose={() => setIsPrefModalOpen(false)}>
          <PreferenceDisplay preferences={selectedMember?.preference || {}} />
        </Modal>
        {group.members && Object.entries(group.members).length > 0 && (
          <div className="rounded-2xl border border-gray-200 p-5">
            <p className="mb-3 text-lg font-bold text-gray-800">
              Individual Preference Breakdown
            </p>

            <div className="flex flex-col gap-4">
              {Object.entries(group.members).map(([id, preference]) => (
                <button
                  key={id}
                  onClick={() => {
                    setSelectedMember({ id, preference });
                    setIsPrefModalOpen(true);
                  }}
                  className="flex cursor-pointer items-center justify-between gap-4 rounded-2xl border border-gray-200 bg-white px-4 py-3 text-left shadow-sm transition-all hover:shadow-md focus:outline-none"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#636AE8] text-white">
                      <User size={18} />
                    </div>

                    <div className="flex flex-col gap-1">
                      <span className="font-medium text-gray-800">
                        {preference.user_name}{" "}
                        {preference.user_name ==
                          localStorage.getItem("username") && (
                          <span className="ml-2 text-xs text-gray-400">
                            (YOU)
                          </span>
                        )}
                        {group.createdBy == id && (
                          <Crown className="ml-5 inline-block size-5 text-yellow-400" />
                        )}
                      </span>

                      <span className="text-sm text-gray-500">
                        Tap to view preferences
                      </span>
                    </div>
                  </div>

                  <ArrowRight className="text-gray-400" size={18} />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-10 lg:w-2/3">
        <div className="h-150 overflow-hidden rounded-2xl">
          <Map />
        </div>

        <div>
          <p className="mb-5 text-2xl font-[700]">Top Group picks</p>
          {groupRecommendations.length > 0 ? (
            <>
              <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
                {paginatedGroupItems.map((data) => (
                  <RestaurantCard key={data.restaurant_id} data={data} />
                ))}
              </div>

              <div className="mt-6 flex justify-center">
                <Pagination
                  count={Math.ceil(
                    groupRecommendations.length / groupItemsPerPage,
                  )}
                  page={groupPage}
                  onChange={handleGroupPageChange}
                  sx={{
                    "& .Mui-selected": {
                      backgroundColor: "#636AE8",
                      color: "#fff",
                      "&:hover": {
                        backgroundColor: "#5a61d1",
                      },
                    },
                    "& .MuiPaginationItem-root": {
                      borderRadius: "8px",
                    },
                  }}
                />
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-gray-200 py-10 text-center">
              <Users2 className="h-10 w-10 text-[#636AE8]" />
              <p className="max-w-md font-semibold text-gray-800 lg:text-lg">
                Choose your preference and get your recommendation!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
