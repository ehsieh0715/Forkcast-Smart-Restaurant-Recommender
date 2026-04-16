export default function FeatureCard({ Icon, heading, description }) {
  return (
    <div className="flex flex-col p-[24px]">
      <Icon />
      <p className="my-3 font-[800]">{heading}</p>
      <p className="text-[#8C8D8B]">{description}</p>
    </div>
  );
}
