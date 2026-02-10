"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL, fetchAPI } from "@/lib/api";

export default function Home() {
  const [apiStatus, setApiStatus] = useState<string>("checking...");

  useEffect(() => {
    fetchAPI("/health")
      .then((data) => setApiStatus(data.status))
      .catch(() => setApiStatus("disconnected"));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Senate
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          FastAPI + Next.js + SQL Server
        </p>
        <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
          <div className="flex items-center justify-between">
            <span className="text-gray-700">API Status:</span>
            <span
              className={`font-semibold ${
                apiStatus === "healthy"
                  ? "text-green-600"
                  : apiStatus === "checking..."
                    ? "text-yellow-600"
                    : "text-red-600"
              }`}
            >
              {apiStatus}
            </span>
          </div>
        </div>
        <div className="mt-8 space-x-4">
          <a
            href={`${API_BASE_URL}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            API Docs
          </a>
        </div>
      </div>
    </div>
  );
}
