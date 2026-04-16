import { Link } from "react-router-dom";
import { motion as Motion } from "framer-motion";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  show: (custom = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: custom, ease: "easeOut" },
  }),
};

export default function LandingPageHeader() {
  return (
    <header className="relative bg-[url('/LandingpageRestaurant.jpg')] bg-cover bg-center bg-no-repeat px-[5%] py-[72px] sm:py-[92px] lg:py-[110px]">
      {/* Background overlay */}
      <Motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.4 }}
        transition={{ duration: 1 }}
        className="absolute inset-0 bg-black"
      ></Motion.div>

      <div className="relative z-10 text-white">
        <Motion.p
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="my-5 text-center text-3xl font-bold sm:text-5xl md:text-6xl lg:text-8xl"
        >
          Escape the Crowd, Enjoy Your Perfect Bite in NYC
        </Motion.p>

        <Motion.p
          custom={0.2}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mx-auto my-5 w-full text-center opacity-80 sm:text-xl md:w-[60%]"
        >
          Forkcast helps you find peaceful restaurants using smart crowd
          predictions and real-time data.
        </Motion.p>

        <Motion.div
          custom={0.4}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mt-8 flex justify-center"
        >
          <Motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}>
            <Link
              to="login"
              className="rounded-full bg-[#636AE8] px-[25px] py-[12px] text-xs font-[700] text-white shadow-xl transition-colors hover:bg-[rgba(81,120,255,255)] md:text-sm"
            >
              Explore now
            </Link>
          </Motion.div>
        </Motion.div>
      </div>
    </header>
  );
}
