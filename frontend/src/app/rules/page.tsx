"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet, apiPost } from "@/lib/api";

const categoryColors: Record<string, string> = {
  ELIGIBILITY: "bg-blue-100 text-blue-700",
  COVERAGE_LIMIT: "bg-purple-100 text-purple-700",
  WAITING_PERIOD: "bg-yellow-100 text-yellow-700",
  EXCLUSION: "bg-red-100 text-red-700",
  DOCUMENTATION: "bg-green-100 text-green-700",
};

export default function RulesPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRules = () => {
    apiGet("/rules")
      .then((res) => setData(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRules(); }, []);

  const toggleActive = async (rule: any) => {
    try {
      await fetch(`/api/rules/${rule.RULE_ID}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !rule.IS_ACTIVE }),
      });
      fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Claim Rules</h1>
        <Link href="/rules/new" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          + Add Rule
        </Link>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : data.length === 0 ? (
        <p className="text-gray-500">No claim rules found.</p>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-3">ID</th>
                <th className="text-left p-3">Rule Name</th>
                <th className="text-left p-3">Category</th>
                <th className="text-left p-3">Action</th>
                <th className="text-center p-3">Priority</th>
                <th className="text-center p-3">Active</th>
              </tr>
            </thead>
            <tbody>
              {data.map((rule) => (
                <tr key={rule.RULE_ID} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-mono">{rule.RULE_ID}</td>
                  <td className="p-3">
                    <div>{rule.RULE_NAME}</div>
                    {rule.DESCRIPTION && <div className="text-xs text-gray-400">{rule.DESCRIPTION}</div>}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${categoryColors[rule.RULE_CATEGORY] || "bg-gray-100"}`}>
                      {rule.RULE_CATEGORY}
                    </span>
                  </td>
                  <td className="p-3">{rule.ACTION}</td>
                  <td className="p-3 text-center">{rule.PRIORITY}</td>
                  <td className="p-3 text-center">
                    <button
                      onClick={() => toggleActive(rule)}
                      className={`px-3 py-1 rounded text-xs font-medium ${rule.IS_ACTIVE ? "bg-green-100 text-green-700" : "bg-gray-200 text-gray-500"}`}
                    >
                      {rule.IS_ACTIVE ? "Active" : "Inactive"}
                    </button>
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
