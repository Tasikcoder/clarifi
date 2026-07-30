"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "@/lib/api";

export default function NewPolicyholderPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    nama_lengkap: "",
    no_ktp: "",
    tanggal_lahir: "",
    jenis_kelamin: "L",
    alamat: "",
    no_telepon: "",
    email: "",
    tanggal_daftar: new Date().toISOString().split("T")[0],
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await apiPost("/policyholders", form);
      router.push("/policyholders");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="page-title mb-6">Add Policyholder</h1>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="form-label">Full Name *</label>
            <input name="nama_lengkap" value={form.nama_lengkap} onChange={handleChange} required className="form-input" />
          </div>
          <div>
            <label className="form-label">ID Number (NIK) *</label>
            <input name="no_ktp" value={form.no_ktp} onChange={handleChange} required className="form-input" />
          </div>
          <div>
            <label className="form-label">Date of Birth</label>
            <input type="date" name="tanggal_lahir" value={form.tanggal_lahir} onChange={handleChange} className="form-input" />
          </div>
          <div>
            <label className="form-label">Gender</label>
            <select name="jenis_kelamin" value={form.jenis_kelamin} onChange={handleChange} className="form-select">
              <option value="L">Male</option>
              <option value="P">Female</option>
            </select>
          </div>
          <div>
            <label className="form-label">Phone</label>
            <input name="no_telepon" value={form.no_telepon} onChange={handleChange} className="form-input" />
          </div>
          <div>
            <label className="form-label">Email</label>
            <input type="email" name="email" value={form.email} onChange={handleChange} className="form-input" />
          </div>
          <div className="col-span-2">
            <label className="form-label">Address</label>
            <textarea name="alamat" value={form.alamat} onChange={handleChange} rows={2} className="form-textarea" />
          </div>
          <div>
            <label className="form-label">Registration Date</label>
            <input type="date" name="tanggal_daftar" value={form.tanggal_daftar} onChange={handleChange} className="form-input" />
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Saving..." : "Save"}
          </button>
          <button type="button" onClick={() => router.push("/policyholders")} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
