"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";

export default function PolicyholdersPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/policyholders")
      .then((res) => setData(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Policyholders</h1>
        <Link href="/policyholders/new" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          + Add Policyholder
        </Link>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : data.length === 0 ? (
        <p className="text-gray-500">No policyholders found.</p>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-3">ID</th>
                <th className="text-left p-3">Name</th>
                <th className="text-left p-3">ID No.</th>
                <th className="text-left p-3">Phone</th>
                <th className="text-left p-3">Email</th>
                <th className="text-left p-3">Registered</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.POLICYHOLDER_ID} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-mono text-blue-600">{row.POLICYHOLDER_ID}</td>
                  <td className="p-3">{row.NAMA_LENGKAP}</td>
                  <td className="p-3">{row.NO_KTP}</td>
                  <td className="p-3">{row.NO_TELEPON || "-"}</td>
                  <td className="p-3">{row.EMAIL || "-"}</td>
                  <td className="p-3 text-gray-500">{row.TANGGAL_DAFTAR}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
