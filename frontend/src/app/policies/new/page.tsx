"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiPost, apiGet } from "@/lib/api";

export default function NewPolicyPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [policyholders, setPolicyholders] = useState<any[]>([]);

  const [form, setForm] = useState({
    policyholder_id: "",
    plan_type: "INDIVIDU",
    coverage_limit: "",
    effective_date: "",
    expiry_date: "",
    exclusions: "",
    premi_bulanan: "",
    status: "ACTIVE",
  });

  useEffect(() => {
    apiGet("/policyholders").then((res) => setPolicyholders(res.data || [])).catch(console.error);
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        coverage_limit: parseFloat(form.coverage_limit) || 0,
        premi_bulanan: parseFloat(form.premi_bulanan) || 0,
        exclusions: form.exclusions ? form.exclusions.split(",").map((s) => s.trim()) : [],
      };
      await apiPost("/policies", payload);
      router.push("/policies");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="page-title mb-6">Add Policy</h1>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="form-label">Policyholder *</label>
            <select name="policyholder_id" value={form.policyholder_id} onChange={handleChange} required className="form-select">
              <option value="">-- Select Policyholder --</option>
              {policyholders.map((ph) => (
                <option key={ph.POLICYHOLDER_ID} value={ph.POLICYHOLDER_ID}>
                  {ph.POLICYHOLDER_ID} - {ph.NAMA_LENGKAP}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Plan Type *</label>
            <select name="plan_type" value={form.plan_type} onChange={handleChange} className="form-select">
              <option value="INDIVIDU">Individual</option>
              <option value="KELUARGA">Family</option>
              <option value="KORPORAT">Corporate</option>
            </select>
          </div>
          <div>
            <label className="form-label">Coverage Limit (Rp) *</label>
            <input type="number" name="coverage_limit" value={form.coverage_limit} onChange={handleChange} required className="form-input" placeholder="100000000" />
          </div>
          <div>
            <label className="form-label">Effective Date *</label>
            <input type="date" name="effective_date" value={form.effective_date} onChange={handleChange} required className="form-input" />
          </div>
          <div>
            <label className="form-label">Expiry Date *</label>
            <input type="date" name="expiry_date" value={form.expiry_date} onChange={handleChange} required className="form-input" />
          </div>
          <div>
            <label className="form-label">Monthly Premium (Rp)</label>
            <input type="number" name="premi_bulanan" value={form.premi_bulanan} onChange={handleChange} className="form-input" placeholder="500000" />
          </div>
          <div>
            <label className="form-label">Status</label>
            <select name="status" value={form.status} onChange={handleChange} className="form-select">
              <option value="ACTIVE">Active</option>
              <option value="EXPIRED">Expired</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="form-label">Exclusions (comma-separated)</label>
            <textarea name="exclusions" value={form.exclusions} onChange={handleChange} rows={2} className="form-textarea" placeholder="Pre-existing conditions, Cosmetic surgery, Dental" />
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Saving..." : "Save"}
          </button>
          <button type="button" onClick={() => router.push("/policies")} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
