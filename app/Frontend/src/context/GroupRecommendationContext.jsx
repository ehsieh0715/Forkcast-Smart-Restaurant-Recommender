// context/GroupRecommendationContext.js
import { createContext, useState } from "react";

export const GroupRecommendationContext = createContext();

export default function GroupRecommendationProvider({ children }) {
  const [groupRecommendations, setGroupRecommendations] = useState([]);
  const [groupLoading, setGroupLoading] = useState(false);

  const handleGroupRecommendations = (recs) => {
    setGroupRecommendations(recs);
  };

  return (
    <GroupRecommendationContext.Provider
      value={{
        groupRecommendations,
        handleGroupRecommendations,
        groupLoading,
        setGroupLoading,
      }}
    >
      {children}
    </GroupRecommendationContext.Provider>
  );
}
