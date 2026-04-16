export default function LandingPageContent() {
  return (
    <div>
      <section className="flex flex-col gap-10 px-10 py-10">
        <p className="text-center text-xl font-[700] sm:text-2xl md:text-3xl lg:text-4xl">
          Experience QuietBite in Action
        </p>
        <img
          src="/Quitebite.png"
          className="m-auto block w-[100%] max-w-[900px]"
        ></img>
        <p className="text-center text-sm text-[#8C8D8B]">
          Find your next peaceful culinary adventure with our intuitive app
          interface
        </p>
      </section>
      <section className="flex flex-col gap-7 px-10 py-10">
        <p className="text-center text-xl font-[700] sm:text-2xl md:text-3xl lg:text-4xl">
          Ready to Find Your Next Quiet Bite?
        </p>
        <p className="text-center text-sm text-[#8C8D8B]">
          Stop guessing and start enjoying the best of NYC dining, minus the
          noise.
        </p>
      </section>
      <section className="flex flex-col gap-7 px-10 pt-10 pb-20">
        <p className="text-center text-xl font-[700] sm:text-2xl md:text-3xl lg:text-4xl">
          Our Data Sources
        </p>
        <p className="m-auto w-[100%] text-center text-sm text-[#8C8D8B] md:w-[75%] lg:w-[50%]">
          SRR uses a combination of real-time restaurant data, predictive crowd
          algorithms, and user reviews to provide you with the most accurate
          quietness predictions.
        </p>
      </section>
    </div>
  );
}
