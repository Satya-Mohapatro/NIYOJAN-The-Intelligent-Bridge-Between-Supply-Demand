import React from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

interface ForecastItem {
  Product_ID: string;
  Product_Name: string;
  Category: string;
  Last_Week_Sales: number;
  Final_Forecasted_Sales: number[];
}

interface ForecastChartProps {
  data: ForecastItem[];
}

const ForecastChart: React.FC<ForecastChartProps> = ({ data }) => {
  // Transform the backend data into a format Recharts can use
  const chartData = data.map((item) => ({
    name: item.Product_Name,
    week1: item.Final_Forecasted_Sales?.[0] || 0,
    week2: item.Final_Forecasted_Sales?.[1] || 0,
    week3: item.Final_Forecasted_Sales?.[2] || 0,
    week4: item.Final_Forecasted_Sales?.[3] || 0,
  }));

  // In case there's no valid data
  if (!chartData.length) {
    return (
      <div className="p-4 text-gray-400 text-center">
        No forecast data available for chart.
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-900 rounded-2xl shadow-md mt-8">
      <h2 className="text-xl font-semibold text-green-300 mb-4">
        📈 4-Week Forecast Trends
      </h2>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="name" stroke="#ccc" />
          <YAxis stroke="#ccc" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="week1" stroke="#4CAF50" name="Week 1" />
          <Line type="monotone" dataKey="week2" stroke="#FFC107" name="Week 2" />
          <Line type="monotone" dataKey="week3" stroke="#03A9F4" name="Week 3" />
          <Line type="monotone" dataKey="week4" stroke="#E91E63" name="Week 4" />
        </LineChart>
      </ResponsiveContainer>

      <h2 className="text-xl font-semibold text-green-300 mt-10 mb-4">
        📊 Total Forecast per Product
      </h2>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="name" stroke="#ccc" />
          <YAxis stroke="#ccc" />
          <Tooltip />
          <Legend />
          <Bar dataKey="week4" fill="#4CAF50" name="Final Week Forecast" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ForecastChart;
