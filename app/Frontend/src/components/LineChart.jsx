import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

// Register required chart components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
);

// Sample data (in percentage)
const data = {
  labels: ["10 AM", "12 PM", "2 PM", "4 PM", "6 PM", "8 PM", "10 PM"],
  datasets: [
    {
      label: "Crowd Level",
      data: [15, 65, 50, 30, 90, 75, 50],
      borderColor: "#0284c7", // blue-600
      backgroundColor: "rgba(2, 132, 199, 0.1)", // light fill
      fill: false,
      tension: 0.4,
      pointRadius: 0, // Hide points
    },
  ],
};

const options = {
  responsive: true,
  plugins: {
    legend: { display: false },
    title: {
      display: true,
      text: "Hourly Crowd Levels",
      align: "start",
      font: {
        size: 16,
        weight: "bold",
      },
      padding: {
        top: 10,
        bottom: 30, // space below heading
      },
    },
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: {
        callback: (value) => `${value}%`,
        stepSize: 25,
      },
      grid: {
        drawBorder: false,
        color: "#e5e7eb", // gray-200
      },
    },
    x: {
      grid: {
        display: false,
      },
    },
  },
};

const LineChart = () => {
  return <Line data={data} options={options} />;
};

export default LineChart;
