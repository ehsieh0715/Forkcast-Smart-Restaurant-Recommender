import GroupPageContent from "../components/GroupPageContent";
import GroupPageHeader from "../components/GroupPageHeader";
import { useState, useEffect } from "react";
import { Await, useLoaderData } from "react-router-dom";
import { Suspense } from "react";
import BackdropLoader from "../utils/BackdropLoader";
import { getAuthToken } from "../components/Auth";
import { useContext } from "react";
import { GroupRecommendationContext } from "../context/GroupRecommendationContext";
import { redirect } from "react-router-dom";

export default function GroupPage() {
  const { data } = useLoaderData();
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [groups, setGroups] = useState([]);
  useContext(GroupRecommendationContext);

  useEffect(() => {
    let isMounted = true;

    data.then((initialGroups) => {
      if (isMounted) {
        setGroups(initialGroups);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [data]);

  const handleGroupChange = async (e) => {
    const id = e.target.value;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/group/session/${id}/members`,
        {
          headers: { "Content-Type": "application/json" },
          method: "GET",
        },
      );

      const data = await response.json();

      setSelectedGroup({
        id,
        members: data.group.members,
        createdBy: data.group.created_by,
      });
    } catch (err) {
      console.error("Failed to fetch members", err);
    }
  };

  return (
    <>
      <Suspense fallback={<BackdropLoader />}>
        <Await resolve={data}>
          {(initialGroups) => (
            <GroupPageHeader
              group={selectedGroup}
              groups={groups}
              onGroupChange={handleGroupChange}
              setGroups={setGroups}
              setSelectedGroup={setSelectedGroup}
            />
          )}
        </Await>
      </Suspense>

      {selectedGroup && (
        <GroupPageContent group={selectedGroup} setGroup={setSelectedGroup} />
      )}
    </>
  );
}

export async function loader() {
  const token = getAuthToken();
  if (!token) return redirect("/");

  const userId = localStorage.getItem("user");

  return {
    data: fetch(`${import.meta.env.VITE_API_URL}/group/user/${userId}/groups`, {
      headers: { "Content-Type": "application/json" },
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Response("Failed to load groups", {
            status: response.status,
          });
        }
        return response.json();
      })
      .then((result) => result.groups),
  };
}
