"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "@/lib/api";

export default function NewRulePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    rule_name: "",
    rule_category: "ELIGIBILITY",
    action: "FLAG",
    priority: "0",
    is_active: true,
    description: "",
    condition_expression: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      let condExpr = null;
      if (form.condition_expression.trim()) {
        try {
          condExpr = JSON.parse(form.condition_expression);
        } catch {
          setError("Condition expression harus valid JSON");
          setLoading(false);
          return;
        }
      }

      await apiPost("/rules", {
        rule_name: form.rule_name,
        rule_category: form.rule_category,
        action: form.action,
        priority: parseInt(form.priority) || 0,
        is_active: form.is_active,
        description: form.description,
        condition_expression: condExpr,
      });
      router.push("/rules");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="page-title mb-6">Add Claim Rule</h1>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="form-label">Rule Name *</label>
            <input name="rule_name" value={form.rule_name} onChange={handleChange} required className="form-input" placeholder="Waiting period 30 hari" />
          </div>
          <div>
            <label className="form-label">Category *</label>
            <select name="rule_category" value={form.rule_category} onChange={handleChange} className="form-select">
              <option value="ELIGIBILITY">Eligibility</option>
              <option value="COVERAGE_LIMIT">Coverage Limit</option>
              <option value="WAITING_PERIOD">Waiting Period</option>
              <option value="EXCLUSION">Exclusion</option>
              <option value="DOCUMENTATION">Documentation</option>
            </select>
          </div>
          <div>
            <label className="form-label">Action *</label>
            <select name="action" value={form.action} onChange={handleChange} className="form-select">
              <option value="APPROVE">Approve</option>
              <option value="REJECT">Reject</option>
              <option value="FLAG">Flag for Review</option>
            </select>
          </div>
          <div>
            <label className="form-label">Priority</label>
            <input type="number" name="priority" value={form.priority} onChange={handleChange} className="form-input" />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} className="rounded" />
              <span className="text-sm text-gray-600">Aktif</span>
            </label>
          </div>
          <div className="col-span-2">
            <label className="form-label">Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} rows={2} className="form-textarea" placeholder="Penjelasan aturan ini..." />
          </div>
          <div className="col-span-2">
            <label className="form-label">Condition Expression (JSON, optional)</label>
            <textarea name="condition_expression" value={form.condition_expression} onChange={handleChange} rows={3} className="form-textarea font-mono text-xs" placeholder='{"waiting_days": 30, "applies_to": "all"}' />
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Saving..." : "Save"}
          </button>
          <button type="button" onClick={() => router.push("/rules")} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
