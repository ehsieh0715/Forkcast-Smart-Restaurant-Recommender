export default function Checkbox({
  data = [],
  heading,
  selected = [],
  onChange,
}) {
  const toggle = (item) => {
    if (selected.includes(item)) {
      onChange(selected.filter((i) => i !== item));
    } else {
      onChange([...selected, item]);
    }
  };

  return (
    <div className="mb-4">
      <p className="mb-2 font-medium text-gray-600">{heading}</p>
      <div className="grid grid-cols-2 gap-2 md:max-lg:grid-cols-3">
        {data.map((item) => (
          <label key={item} className="text-sm">
            <input
              type="radio"
              checked={selected.includes(item)}
              onChange={() => toggle(item)}
              className="mr-2"
            />
            {item}
          </label>
        ))}
      </div>
    </div>
  );
}
