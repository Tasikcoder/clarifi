"use client";

import { useState, useRef } from "react";
import { apiPost, apiUpload } from "@/lib/api";

type ImportType = "policyholder" | "policy" | "rules";

export default function ImportPage() {
  const [importType, setImportType] = useState<ImportType>("policyholder");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetForm = () => {
    setFile(null);
    setPreview(null);
    setSaved(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleExtract = async () => {
    if (!file) return;
    setLoading(true);
    setPreview(null);
    setSaved(false);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await apiUpload(`/import/${importType}/extract`, formData);
      if (res.status === "rejected") {
        alert(`Document rejected: ${res.message || "Not relevant to insurance claims"}\n\nCategory: ${res.data?.screening?.category || "unknown"}`);
        resetForm();
        return;
      }
      // For rules, handle nested structure
      const data = res.data?.rules || res.data;
      // Remove internal screening metadata before showing to user
      if (data && !Array.isArray(data)) {
        delete data._screening;
      }
      setPreview(data);
    } catch (e: any) {
      alert("Extraction failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!preview) return;

    // Validate: reject if data still contains placeholder text from LLM
    if (importType === "policyholder") {
      if (!preview.nama_lengkap || preview.nama_lengkap.toLowerCase().includes("string")) {
        alert("Please fill in the Full Name field with actual data before saving.");
        return;
      }
      if (preview.tanggal_lahir === "YYYY-MM-DD" || preview.no_ktp?.includes("string")) {
        alert("Some fields still contain placeholder text. Please edit them with actual data before saving.");
        return;
      }
    }

    setSaving(true);
    try {
      if (importType === "policyholder") {
        await apiPost("/policyholders", preview);
      } else if (importType === "policy") {
        const payload = { ...preview };
        delete payload.policyholder_name;
        if (!payload.policyholder_id) {
          alert("Policyholder ID is required. Fill it manually before saving.");
          setSaving(false);
          return;
        }
        await apiPost("/policies", payload);
      } else if (importType === "rules") {
        const rules = Array.isArray(preview) ? preview : [preview];
        for (const rule of rules) {
          const payload = { ...rule };
          if (typeof payload.condition_expression === "string") {
            payload.condition_expression = { description: payload.condition_expression };
          }
          await apiPost("/rules", payload);
        }
      }
      setSaved(true);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (e: any) {
      alert("Save failed: " + e.message);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (key: string, value: any) => {
    if (Array.isArray(preview)) {
      return; // handled by updateRuleField
    }
    setPreview({ ...preview, [key]: value });
  };

  const updateRuleField = (index: number, key: string, value: any) => {
    const updated = [...preview];
    updated[index] = { ...updated[index], [key]: value };
    setPreview(updated);
  };

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Import Data from Documents</h1>

      {/* Type Selection */}
      <div className="flex gap-2 mb-6">
        {[
          { key: "policyholder" as ImportType, label: "Policyholder" },
          { key: "policy" as ImportType, label: "Policy" },
          { key: "rules" as ImportType, label: "Claim Rules" },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => { setImportType(t.key); resetForm(); }}
            className={`px-4 py-2 rounded text-sm font-medium ${
              importType === t.key ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Upload */}
      <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Upload Document (.pdf / .docx)</h2>
        <input
          ref={fileInputRef}
          type="file"
          accept=".docx,.pdf"
          onChange={(e) => { setFile(e.target.files?.[0] || null); setPreview(null); setSaved(false); }}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
        />
        <button
          onClick={handleExtract}
          disabled={!file || loading}
          className="mt-4 px-4 py-2 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 disabled:opacity-50"
        >
          {loading ? "Extracting..." : "Extract & Preview"}
        </button>
      </div>

      {/* Preview & Edit */}
      {preview && !saved && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
          <h2 className="font-semibold text-gray-700 mb-4">
            Preview Data — {importType === "policyholder" ? "Policyholder" : importType === "policy" ? "Policy" : "Rules"}
          </h2>
          <p className="text-xs text-gray-500 mb-4">Edit fields as needed before saving.</p>

          {importType === "policyholder" && (
            <div className="space-y-3">
              {[
                { key: "nama_lengkap", label: "Full Name" },
                { key: "no_ktp", label: "NIK" },
                { key: "tanggal_lahir", label: "Date of Birth" },
                { key: "jenis_kelamin", label: "Gender (M/F)" },
                { key: "alamat", label: "Alamat" },
                { key: "no_telepon", label: "No. Telepon" },
                { key: "email", label: "Email" },
              ].map((f) => (
                <div key={f.key}>
                  <label className="text-xs text-gray-500">{f.label}</label>
                  <input
                    type="text"
                    value={preview[f.key] || ""}
                    onChange={(e) => updateField(f.key, e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm"
                  />
                </div>
              ))}
            </div>
          )}

          {importType === "policy" && (
            <div className="space-y-3">
              {[
                { key: "policyholder_name", label: "Policyholder Name (reference)" },
                { key: "policyholder_id", label: "Policyholder ID (fill manually)" },
                { key: "plan_type", label: "Plan Type" },
                { key: "coverage_limit", label: "Limit Pertanggungan" },
                { key: "effective_date", label: "Effective Date" },
                { key: "expiry_date", label: "Expiry Date" },
                { key: "premi_bulanan", label: "Monthly Premium" },
              ].map((f) => (
                <div key={f.key}>
                  <label className="text-xs text-gray-500">{f.label}</label>
                  <input
                    type="text"
                    value={preview[f.key] || ""}
                    onChange={(e) => updateField(f.key, f.key === "coverage_limit" || f.key === "premi_bulanan" ? Number(e.target.value) || e.target.value : e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm"
                  />
                </div>
              ))}
              <div>
                <label className="text-xs text-gray-500">Exclusions</label>
                <input
                  type="text"
                  value={Array.isArray(preview.exclusions) ? preview.exclusions.join("; ") : preview.exclusions || ""}
                  onChange={(e) => updateField("exclusions", e.target.value.split(";").map((s: string) => s.trim()))}
                  className="w-full border rounded px-3 py-2 text-sm"
                />
                <p className="text-xs text-gray-400">Separate with semicolons (;)</p>
              </div>
            </div>
          )}

          {importType === "rules" && Array.isArray(preview) && (
            <div className="space-y-6">
              {preview.map((rule: any, idx: number) => (
                <div key={idx} className="border rounded p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Rule {idx + 1}</h3>
                  {[
                    { key: "rule_name", label: "Rule Name" },
                    { key: "rule_category", label: "Kategori" },
                    { key: "condition_expression", label: "Condition" },
                    { key: "action", label: "Aksi (APPROVE/REJECT/FLAG)" },
                    { key: "priority", label: "Prioritas" },
                    { key: "description", label: "Description" },
                  ].map((f) => (
                    <div key={f.key} className="mb-2">
                      <label className="text-xs text-gray-500">{f.label}</label>
                      <input
                        type="text"
                        value={rule[f.key] || ""}
                        onChange={(e) => updateRuleField(idx, f.key, f.key === "priority" ? Number(e.target.value) || 0 : e.target.value)}
                        className="w-full border rounded px-3 py-1.5 text-sm"
                      />
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            className="mt-6 px-6 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save to Database"}
          </button>
        </div>
      )}

      {/* Success */}
      {saved && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <p className="text-green-700 font-medium">Data saved successfully!</p>
          <p className="text-green-600 text-sm mt-1">
            {importType === "policyholder" && "View in Policyholders page."}
            {importType === "policy" && "View in Policies page."}
            {importType === "rules" && "View in Rules page."}
          </p>
          <button
            onClick={resetForm}
            className="mt-3 px-4 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
          >
            Import Another Document
          </button>
        </div>
      )}
    </div>
  );
}
