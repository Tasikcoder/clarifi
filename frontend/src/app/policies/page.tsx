"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";

const statusColors: Record<string, string> = {
  ACTIVE: "bg-green-100 text-green-700",
  EXPIRED: "bg-gray-100 text-gray-700",
  CANCELLED: "bg-red-100 text-red-700",
};

export default function PoliciesPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/policies")
      .then((res) => setData(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Policies</h1>
        <Link href="/policies/new" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          + Add Policy
        </Link>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : data.length === 0 ? (
        <p className="text-gray-500">No policies found.</p>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-3">Policy ID</th>
                <th className="text-left p-3">Holder</th>
                <th className="text-left p-3">Plan</th>
                <th className="text-right p-3">Limit (Rp)</th>
                <th className="text-left p-3">Effective</th>
                <th className="text-left p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.POLICY_ID} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-mono text-blue-600">{row.POLICY_ID}</td>
                  <td className="p-3">{row.POLICYHOLDER_NAME || row.POLICYHOLDER_ID}</td>
                  <td className="p-3">{row.PLAN_TYPE}</td>
                  <td className="p-3 text-right">{row.COVERAGE_LIMIT?.toLocaleString("id-ID")}</td>
                  <td className="p-3 text-gray-500">{row.EFFECTIVE_DATE} - {row.EXPIRY_DATE}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[row.STATUS] || "bg-gray-100"}`}>
                      {row.STATUS}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
