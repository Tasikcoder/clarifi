"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";

interface Claim {
  CLAIM_ID: string;
  PATIENT_NAME: string;
  NAMA_PROVIDER: string;
  JENIS_LAYANAN: string;
  STATUS: string;
  TOTAL_AMOUNT: number;
  TANGGAL_PENGAJUAN: string;
}

const statusColors: Record<string, string> = {
  SUBMITTED: "bg-blue-100 text-blue-700",
  MANUAL_REVIEW: "bg-yellow-100 text-yellow-700",
  PENDING_CLARIFICATION: "bg-orange-100 text-orange-700",
  APPROVED_WITH_CONDITIONS: "bg-indigo-100 text-indigo-700",
  AUTO_APPROVED: "bg-green-100 text-green-700",
  APPROVED: "bg-green-100 text-green-700",
  AUTO_REJECTED: "bg-red-100 text-red-700",
  REJECTED: "bg-red-100 text-red-700",
};

export default function ClaimsListPage() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("ALL");

  useEffect(() => {
    apiGet("/claims")
      .then((res) => setClaims(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filteredClaims = filter === "ALL" ? claims : claims.filter((c) => c.STATUS === filter);
  const statusCounts = claims.reduce((acc, c) => { acc[c.STATUS] = (acc[c.STATUS] || 0) + 1; return acc; }, {} as Record<string, number>);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Claims List</h1>
        <Link
          href="/claims/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          + New Claim
        </Link>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {["ALL", "SUBMITTED", "MANUAL_REVIEW", "PENDING_CLARIFICATION", "APPROVED_WITH_CONDITIONS", "APPROVED", "REJECTED"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded text-xs font-medium ${filter === s ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            {s === "ALL" ? `All (${claims.length})` : `${s} (${statusCounts[s] || 0})`}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : filteredClaims.length === 0 ? (
        <p className="text-gray-500">No claims found with this status.</p>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-3">Claim ID</th>
                <th className="text-left p-3">Patient</th>
                <th className="text-left p-3">Provider</th>
                <th className="text-left p-3">Layanan</th>
                <th className="text-right p-3">Total (Rp)</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredClaims.map((claim) => (
                <tr key={claim.CLAIM_ID} className="border-t hover:bg-gray-50">
                  <td className="p-3">
                    <Link href={`/claims/${claim.CLAIM_ID}`} className="text-blue-600 hover:underline">
                      {claim.CLAIM_ID}
                    </Link>
                  </td>
                  <td className="p-3">{claim.PATIENT_NAME}</td>
                  <td className="p-3">{claim.NAMA_PROVIDER}</td>
                  <td className="p-3">{claim.JENIS_LAYANAN}</td>
                  <td className="p-3 text-right">{claim.TOTAL_AMOUNT?.toLocaleString("id-ID")}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[claim.STATUS] || "bg-gray-100"}`}>
                      {claim.STATUS}
                    </span>
                  </td>
                  <td className="p-3 text-gray-500">{claim.TANGGAL_PENGAJUAN}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
