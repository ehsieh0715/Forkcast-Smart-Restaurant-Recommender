import { createContext } from "react";
import { useState } from "react";

export const SoloRecommendationContext = createContext();

export default function SoloRecommendationContextProvider({ children }) {
  const [recommendations, setRecommendations] = useState([]);

  const handleRecommendations = (recommendation) => {
    setRecommendations(recommendation);
  };

  return (
    <SoloRecommendationContext.Provider
      value={{ recommendations, handleRecommendations }}
    >
      {children}
    </SoloRecommendationContext.Provider>
  );
}
