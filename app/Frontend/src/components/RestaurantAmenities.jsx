export default function RestaurantAmenities({ data }) {
  return (
    <div className="h-full rounded-2xl border border-gray-200 p-5">
      <h1 className="mb-5 text-xl font-[500]">Amenities</h1>
      <div className="flex flex-wrap gap-3 text-xs font-[500]">
        {(data.amenities ?? []).map((item, index) => (
          <p
            className="rounded-2xl border border-gray-200 bg-gray-100 px-5 py-2"
            key={index}
          >
            {item}
          </p>
        ))}
        {!data.amenities && <p className="px-1 text-gray-400">Unavailable</p>}
      </div>
    </div>
  );
}
