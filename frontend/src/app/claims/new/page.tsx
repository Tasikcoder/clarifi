"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import LineItemsTable from "@/components/LineItemsTable";
import FileUpload from "@/components/FileUpload";
import { apiPost, apiUpload } from "@/lib/api";

interface LineItem {
  item_no: number;
  deskripsi: string;
  kode: string;
  biaya: number;
  catatan: string;
}

export default function NewClaimPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    policy_id: "",
    patient_id: "",
    patient_name: "",
    tanggal_kejadian: "",
    tanggal_pengajuan: new Date().toISOString().split("T")[0],
    jenis_layanan: "RAWAT_JALAN",
    nama_provider: "",
    diagnosis_awal: "",
  });

  const [lineItems, setLineItems] = useState<LineItem[]>([
    { item_no: 1, deskripsi: "", kode: "", biaya: 0, catatan: "" },
  ]);

  const [files, setFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState<{ name: string; status: string; docType?: string }[]>([]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // 1. Submit claim
      const result = await apiPost("/claims", {
        ...form,
        line_items: lineItems.filter((item) => item.deskripsi),
      });

      const claimId = result.data?.claim?.CLAIM_ID || result.data?.claim?.claim_id;

      // 2. Upload documents
      if (claimId && files.length > 0) {
        const statuses: { name: string; status: string; docType?: string }[] = [];
        for (const file of files) {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("document_type", guessDocType(file.name));
          try {
            const uploadRes = await apiUpload(`/claims/${claimId}/documents`, formData);
            statuses.push({
              name: file.name,
              status: uploadRes.data?.parse_status || "UPLOADED",
              docType: uploadRes.data?.detected_doc_type,
            });
          } catch {
            statuses.push({ name: file.name, status: "FAILED" });
          }
          setUploadStatus([...statuses]);
        }
        // Brief delay to show results before redirect
        await new Promise((r) => setTimeout(r, 1500));
      }

      router.push("/claims");
    } catch (err: any) {
      setError(err.message || "Failed to submit claim");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <h1 className="page-title mb-6">Submit New Claim</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header Klaim */}
        <div className="card">
          <h2 className="section-title mb-4">Claim Data</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Policy ID</label>
              <input
                name="policy_id"
                value={form.policy_id}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="POL-001"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
              <input
                name="patient_id"
                value={form.patient_id}
                onChange={handleChange}
                required
                className="form-input"
                placeholder="PAT-001"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Patient Name</label>
              <input
                name="patient_name"
                value={form.patient_name}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider Name (Hospital/Clinic)</label>
              <input
                name="nama_provider"
                value={form.nama_provider}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Incident Date</label>
              <input
                type="date"
                name="tanggal_kejadian"
                value={form.tanggal_kejadian}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Submission Date</label>
              <input
                type="date"
                name="tanggal_pengajuan"
                value={form.tanggal_pengajuan}
                onChange={handleChange}
                required
                className="form-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
              <select
                name="jenis_layanan"
                value={form.jenis_layanan}
                onChange={handleChange}
                className="form-input"
              >
                <option value="RAWAT_JALAN">Outpatient</option>
                <option value="RAWAT_INAP">Inpatient</option>
                <option value="EMERGENCY">Emergency</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Initial Diagnosis (optional)</label>
              <input
                name="diagnosis_awal"
                value={form.diagnosis_awal}
                onChange={handleChange}
                className="form-input"
                placeholder="Appendicitis Acute"
              />
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className="card">
          <LineItemsTable items={lineItems} onChange={setLineItems} />
        </div>

        {/* File Upload */}
        <div className="card">
          <FileUpload files={files} onChange={setFiles} />
          {uploadStatus.length > 0 && (
            <div className="mt-3 space-y-1">
              {uploadStatus.map((s, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span className={`w-2 h-2 rounded-full ${
                    s.status === "PARSED" ? "bg-green-500" :
                    s.status === "REJECTED" ? "bg-orange-500" :
                    s.status === "FAILED" ? "bg-red-500" :
                    "bg-yellow-500"
                  }`}></span>
                  <span>{s.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    s.status === "PARSED" ? "bg-green-100 text-green-700" :
                    s.status === "REJECTED" ? "bg-orange-100 text-orange-700" :
                    s.status === "FAILED" ? "bg-red-100 text-red-700" :
                    "bg-yellow-100 text-yellow-700"
                  }`}>{s.status}</span>
                  {s.docType && s.docType !== "unknown" && (
                    <span className="text-xs text-indigo-600">{s.docType}</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit */}
        <div className="flex gap-3">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Submitting..." : "Submit Claim"}
          </button>
          <button type="button" onClick={() => router.push("/claims")} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

function guessDocType(filename: string): string {
  const lower = filename.toLowerCase();
  if (lower.includes("invoice") || lower.includes("bukti")) return "INVOICE";
  if (lower.includes("form") || lower.includes("formulir")) return "CLAIM_FORM";
  if (lower.includes("medical") || lower.includes("report") || lower.includes("resume"))
    return "MEDICAL_REPORT";
  return "OTHER";
}
