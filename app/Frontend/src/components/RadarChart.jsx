import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

import { Radar } from "react-chartjs-2";

// Register the required components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
);

const data = {
  labels: ["Speed", "Strength", "Stamina", "Agility", "Skill", "Luck"],
  datasets: [
    {
      label: "Player A",
      data: [65, 59, 90, 81, 56, 55],
      backgroundColor: "rgba(99, 102, 241, 0.2)",
      borderColor: "rgba(99, 102, 241, 1)",
      borderWidth: 2,
      pointBackgroundColor: "rgba(99, 102, 241, 1)",
    },
  ],
};

const options = {
  responsive: true,
  scales: {
    r: {
      angleLines: {
        display: true,
      },
      min: 0,
      max: 100,
      ticks: {
        stepSize: 25,
        callback: (value) => {
          return [25, 50, 75, 100].includes(value) ? value : "";
        },
      },
    },
  },
};

export default function RadarChart() {
  return <Radar data={data} options={options} />;
}
