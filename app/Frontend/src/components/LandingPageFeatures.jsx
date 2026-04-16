import FeatureCard from "./FeatureCard";
import { User, FilterIcon, Users, GitCompare } from "lucide-react";

export default function LandingPageFeatures() {
  return (
    <section className="my-10 flex flex-col items-center justify-center gap-5 p-5 lg:flex-row">
      <div>
        <p className="m-auto w-2/3 text-center text-xl font-[800] tracking-wider sm:text-2xl md:text-3xl lg:m-20 lg:w-75 lg:text-left lg:text-4xl lg:leading-12">
          Key Features for Your Urban Dining Experience
        </p>
      </div>
      <div className="m-auto grid max-w-[400px] grid-cols-1 sm:max-w-[800px] sm:grid-cols-2">
        <FeatureCard
          Icon={FilterIcon}
          heading={"Filter by preferences"}
          description={
            "Narrow down restaurants based on your dietary needs, cuisine choices, and budget."
          }
        />
        <FeatureCard
          Icon={User}
          heading={"Personalized Recommendation"}
          description={
            "Get tailored suggestions based on your preferences, past visits, and real-time crowd predictions for a perfect dining experience."
          }
        />
        <FeatureCard
          Icon={Users}
          heading={"Effortless Group dining"}
          description={
            "Easily coordinate with friends, vote on options, and book tables that suit everyone's tastes and preferred noise levels."
          }
        />
        <FeatureCard
          Icon={GitCompare}
          heading={"Smart Restaurant Comparison"}
          description={
            "Compare venues side-by-side on predicted busyness, ratings, cuisine, and amenities to make informed decisions."
          }
        />
      </div>
    </section>
  );
}
