import { Clipboard, Key, Trash, User2 } from "lucide-react";
import { CirclePlus, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { useMediaQuery } from "../hooks/useMediaQuery";
import Modal from "./Modal";
import toast from "react-hot-toast";
import { Select, MenuItem, FormControl, InputLabel } from "@mui/material";
import BackdropLoader from "../utils/BackdropLoader";

export default function GroupPageHeader({
  group,
  groups,
  onGroupChange,
  setGroups,
  setSelectedGroup,
}) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const isLargeScreen = useMediaQuery("(min-width: 1024px)");

  const handleFilterClick = () => {
    setIsModalOpen(!isModalOpen);
  };

  useEffect(() => {
    setIsModalOpen(false);
    setIsJoinModalOpen(false);
  }, [isLargeScreen]);

  useEffect(() => {
    document.body.style.overflow =
      isModalOpen || isJoinModalOpen ? "hidden" : "auto";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isModalOpen, isJoinModalOpen]);

  const handleCreateGroup = async (event) => {
    event.preventDefault();
    setLoading(true);
    const formData = new FormData(event.target);
    const groupName = formData.get("groupName");
    setIsModalOpen(false);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/group/session/create`,
        {
          method: "POST",
          body: JSON.stringify({
            group_name: groupName,
            created_by: localStorage.getItem("user"),
          }),
          headers: { "Content-Type": "application/json" },
        },
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to create group.");
      }

      const newGroup = await response.json();

      toast.success("Group created successfully!");

      setGroups((prevGroups) => [
        ...prevGroups,
        {
          group_id: newGroup.group_id,
          group_name: groupName,
        },
      ]);

      const userId = localStorage.getItem("user");
      const userName = localStorage.getItem("username");

      setSelectedGroup({
        id: newGroup.group_id,
        name: groupName,
        members: {
          [userId]: { user_name: userName },
        },
        createdBy: userId,
      });
    } catch (error) {
      console.error(error);
      toast.error(`Could not create group: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGroup = async (e) => {
    e.preventDefault();
    setLoading(true);

    const groupCode = e.target.groupCode.value.trim();
    const userId = localStorage.getItem("user");
    setIsJoinModalOpen(false);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/group/session/${groupCode}/join`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: userId || undefined,
            preferences: {},
          }),
        },
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Failed to join group.");
      }

      toast.success("Successfully joined group!");

      setGroups((prevGroups) => [
        ...prevGroups,
        {
          group_id: groupCode,
          group_name: result.group.group_name || "Joined Group",
        },
      ]);

      setSelectedGroup({
        id: groupCode,
        name: result.group.group_name,
        members: result.group.members || {},
        createdBy: result.group.created_by,
      });
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGroup = async () => {
    if (!group?.id) return;

    const confirmDelete = window.confirm(
      "Are you sure you want to delete this group?",
    );
    if (!confirmDelete) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/group/session/${group.id}`,
        {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
        },
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Failed to delete group.");
      }

      toast.success("Group deleted successfully.");
      setGroups((prev) => prev.filter((g) => g.group_id !== group.id));
      setSelectedGroup("");
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {loading && <BackdropLoader />}

      <div className="mx-6 my-5 flex items-center justify-between gap-4 md:mx-10 md:flex-row">
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="group-select-label">Select a group</InputLabel>
          <Select
            labelId="group-select-label"
            id="group-select"
            value={group ? group.id : ""}
            label="Select a group"
            onChange={onGroupChange}
          >
            <MenuItem value="" disabled>
              Select a group...
            </MenuItem>
            {groups.map((group) => (
              <MenuItem key={group.group_id} value={group.group_id}>
                {group.group_name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <div className="flex items-center gap-2 md:flex-row">
          <button
            onClick={handleFilterClick}
            title="Create Group"
            className="flex cursor-pointer items-center gap-2 rounded-lg bg-[#636AE8] px-4 py-2 text-sm text-white transition hover:opacity-90"
          >
            <CirclePlus className="size-5" />
            <span className="hidden md:block">Create New Group</span>
          </button>
          <button
            onClick={() => setIsJoinModalOpen(true)}
            title="Join with Code"
            className="flex cursor-pointer items-center gap-2 rounded-lg border-2 border-[#E8618C] px-4 py-2 text-sm text-[#E8618C] transition hover:bg-[#fff0f5]"
          >
            <Key className="size-4" />
            <span className="hidden md:block">Join with code</span>
          </button>
        </div>
      </div>

      <Modal open={isModalOpen} onClose={handleFilterClick}>
        <form
          className="m-auto w-full max-w-md space-y-4 rounded-xl bg-white p-6"
          onSubmit={handleCreateGroup}
        >
          <h2 className="text-xl font-semibold text-gray-800">
            Create a New Group
          </h2>
          <div className="flex flex-col">
            <label
              htmlFor="groupName"
              className="mb-1 text-sm font-medium text-gray-700"
            >
              Group Name
            </label>
            <input
              id="groupName"
              type="text"
              name="groupName"
              required
              placeholder="e.g. Friday Dinner Crew"
              className="rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-[#636AE8] focus:ring-1 focus:ring-[#636AE8] focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="w-full cursor-pointer rounded-md bg-[#636AE8] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#4f51d6]"
          >
            Create Group
          </button>
        </form>
      </Modal>

      <Modal open={isJoinModalOpen} onClose={() => setIsJoinModalOpen(false)}>
        <form
          className="m-auto w-full max-w-md space-y-4 rounded-xl bg-white p-6"
          onSubmit={handleJoinGroup}
        >
          <h2 className="text-xl font-semibold text-gray-800">Join a Group</h2>
          <div className="flex flex-col">
            <label
              htmlFor="groupCode"
              className="mb-1 text-sm font-medium text-gray-700"
            >
              Enter Group Code
            </label>
            <input
              id="groupCode"
              name="groupCode"
              required
              type="text"
              placeholder="e.g. ABC123"
              className="rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-[#E8618C] focus:ring-1 focus:ring-[#E8618C] focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="w-full cursor-pointer rounded-md bg-[#E8618C] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#dc517c]"
          >
            Join Group
          </button>
        </form>
      </Modal>

      <header className="mx-6 mb-10 rounded-2xl border-2 border-gray-200 p-6 text-center md:mx-10 md:text-left">
        {group ? (
          <>
            <div className="mb-3 flex flex-col items-start justify-start gap-2 text-xl font-bold md:flex-row md:items-center md:justify-between md:text-2xl lg:text-3xl">
              {/* Group ID, Copy, Trash (mobile) */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="break-all">
                  Your dining group id: {group.id}
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(group.id);
                      toast.success("Code Copied to clipboard!");
                    }}
                    className="ml-2 cursor-pointer rounded p-1 text-gray-500 transition hover:bg-gray-100 hover:text-black"
                    title="Copy Group ID"
                  >
                    <Clipboard className="size-5 text-inherit" />
                  </button>
                  {/* Trash for mobile only */}
                  <button
                    onClick={handleDeleteGroup}
                    className="ml-2 inline cursor-pointer rounded p-1 text-gray-500 transition hover:bg-gray-100 hover:text-red-600 lg:hidden"
                    title="Delete group"
                  >
                    <Trash className="size-5 text-inherit" />
                  </button>
                </span>
              </div>

              {/* Trash for desktop only */}
              <button
                onClick={handleDeleteGroup}
                className="hidden cursor-pointer rounded p-1 text-gray-500 transition hover:bg-gray-100 hover:text-red-600 lg:block"
                title="Delete group"
              >
                <Trash className="size-5 text-inherit" />
              </button>
            </div>

            <div className="flex flex-col gap-6 md:flex-row md:justify-between">
              <p className="text-sm text-gray-600 md:w-1/4 md:text-[15px]">
                Collaborate with your friends to find the perfect restaurant for
                your next outing.
              </p>
              <div className="flex flex-col items-center gap-2 md:items-end">
                <h2 className="text-sm font-semibold text-gray-800 md:text-base">
                  Current Group Members
                </h2>
                <div className="flex -space-x-2">
                  {group.members && Object.keys(group.members).length > 0 ? (
                    Object.keys(group.members).map((userId) => (
                      <div
                        key={userId}
                        className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200"
                      >
                        <User2 className="h-4 w-4 text-gray-500" />
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-gray-400">No members yet</p>
                  )}
                </div>
                <p className="text-xs text-gray-500">
                  Share the code to invite more friends!
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center gap-4 py-10 text-center">
            <Users className="h-10 w-10 text-[#636AE8]" />
            <p className="max-w-md font-semibold text-gray-800 lg:text-xl">
              Select a group or create one to start dining together!
            </p>
          </div>
        )}
      </header>
    </>
  );
}
