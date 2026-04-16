import { Link } from "react-router-dom";
import { User, Users, GitCompare } from "lucide-react";
import { motion as Motion } from "framer-motion";

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.4,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
};

const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
};

export default function HomePageHeader() {
  const features = [
    {
      icon: (
        <User className="my-2 text-indigo-500 transition-colors duration-200 group-hover:text-white" />
      ),
      label: "Solo Recommendation",
      to: "/solo",
    },
    {
      icon: (
        <Users className="my-2 text-indigo-500 transition-colors duration-200 group-hover:text-white" />
      ),
      label: "Group Recommendation",
      to: "/group",
    },
    {
      icon: (
        <GitCompare className="my-2 text-indigo-500 transition-colors duration-200 group-hover:text-white" />
      ),
      label: "Restaurant Compare",
      to: "/compare",
    },
  ];

  return (
    <header className="relative mb-5 rounded-md bg-[url('/homepage2.svg')] bg-cover bg-center bg-repeat px-[5%] py-[72px] sm:py-[92px] lg:py-[110px]">
      <div className="relative z-10">
        <Motion.p
          variants={fadeInUp}
          initial="hidden"
          animate="show"
          className="my-5 text-center text-3xl font-bold text-[#242524] sm:text-5xl md:text-6xl lg:text-7xl"
        >
          Discover Your Next Favorite Meal
        </Motion.p>

        <Motion.p
          variants={fadeInUp}
          initial="hidden"
          animate="show"
          transition={{ delay: 0.2 }}
          className="mx-auto my-5 w-full text-center text-gray-600 sm:text-xl md:w-[50%]"
        >
          <span className="font-[900] text-[#636AE8]">Forkcast</span> helps you
          find the perfect dining experience, whether you're dining solo, with a
          group, or simply comparing options.
        </Motion.p>

        <Motion.div
          className="m-auto hidden w-[80%] grid-cols-3 gap-3 text-sm lg:grid"
          variants={containerVariants}
          initial="hidden"
          animate="show"
        >
          {features.map((item) => (
            <Motion.div key={item.label} variants={cardVariants}>
              <Link
                to={item.to}
                className="group flex w-full max-w-[250px] cursor-pointer flex-col items-center justify-center justify-self-center rounded-2xl bg-white p-2 shadow-lg transition-colors duration-200 ease-in hover:bg-[#636AE8] hover:text-white lg:p-3"
              >
                {item.icon}
                <p className="font-[700]">{item.label}</p>
              </Link>
            </Motion.div>
          ))}
        </Motion.div>
      </div>
    </header>
  );
}
