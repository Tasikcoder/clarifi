"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

export default function Home() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    apiGet("/adjudication/summary/adjudications")
      .then((res) => setSummary(res.data))
      .catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Dashboard</h1>
      <p className="text-gray-600 mb-8">
        ClariFi — Decision Support System for Health Insurance Claim Adjudication.
      </p>

      {/* Adjudication Summary */}
      <h2 className="text-lg font-semibold text-gray-700 mb-4">Adjudication Summary</h2>
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Total Adjudications</p>
          <p className="text-3xl font-bold text-blue-700">{summary?.total ?? "-"}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Auto-Approve</p>
          <p className="text-3xl font-bold text-green-600">{summary?.approved ?? "-"}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Manual Review</p>
          <p className="text-3xl font-bold text-yellow-600">{summary?.review ?? "-"}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Auto-Reject</p>
          <p className="text-3xl font-bold text-red-600">{summary?.rejected ?? "-"}</p>
        </div>
      </div>

      {/* Average Score */}
      {summary && summary.total > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border max-w-sm">
          <p className="text-sm text-gray-500 mb-2">Average Score</p>
          <div className="flex items-center gap-4">
            <p className="text-4xl font-bold text-indigo-700">{summary.avg_score}</p>
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 rounded-full bg-indigo-500"
                  style={{ width: `${summary.avg_score}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">out of 100</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
