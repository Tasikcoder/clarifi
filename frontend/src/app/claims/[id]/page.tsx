"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiGet, apiPost } from "@/lib/api";

export default function ClaimDetailPage() {
  const params = useParams();
  const claimId = params.id as string;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [adjudication, setAdjudication] = useState<any>(null);
  const [adjLoading, setAdjLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [workflow, setWorkflow] = useState<any>(null);
  const [decisionForm, setDecisionForm] = useState({ decision: "", reason: "", conditions: "", approvedAmount: "" });
  const [clarificationText, setClarificationText] = useState("");
  const [similarClaims, setSimilarClaims] = useState<any[]>([]);

  useEffect(() => {
    if (!claimId) return;
    apiGet(`/claims/${claimId}`)
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));

    // Load existing adjudication if any
    apiGet(`/adjudication/${claimId}/adjudication`)
      .then((res) => setAdjudication(res.data))
      .catch(() => {});

    // Load existing analysis if any
    apiGet(`/analysis/${claimId}/analysis`)
      .then((res) => setAnalysis(res.data))
      .catch(() => {});

    // Load workflow history
    apiGet(`/decisions/${claimId}/history`)
      .then((res) => setWorkflow(res.data))
      .catch(() => {});

    // Load similar claims (Cortex Search)
    apiGet(`/adjudication/${claimId}/similar`)
      .then((res) => setSimilarClaims(res.data || []))
      .catch(() => {});
  }, [claimId]);

  const runAdjudication = async () => {
    setAdjLoading(true);
    try {
      const res = await apiPost(`/adjudication/${claimId}/adjudicate`, {});
      setAdjudication(res.data);
    } catch (e: any) {
      alert("Failed to run adjudication: " + e.message);
    } finally {
      setAdjLoading(false);
    }
  };

  const runAnalysis = async () => {
    setAnalysisLoading(true);
    try {
      const res = await apiPost(`/analysis/${claimId}/analyze-documents`, {});
      setAnalysis({ extraction: { extracted_data: res.data.extracted_facts }, suggestions: res.data.suggestions });
    } catch (e: any) {
      alert("Failed to analyze documents: " + e.message);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleSuggestionDecision = async (suggestionId: string, decision: string) => {
    try {
      await apiPost(`/analysis/suggestions/${suggestionId}?decision=${decision}`, {});
      // Reload analysis
      const res = await apiGet(`/analysis/${claimId}/analysis`);
      setAnalysis(res.data);
    } catch (e: any) {
      alert("Failed to update decision: " + e.message);
    }
  };

  const reloadWorkflow = async () => {
    try {
      const res = await apiGet(`/decisions/${claimId}/history`);
      setWorkflow(res.data);
    } catch {}
  };

  const handleDecision = async () => {
    if (!decisionForm.decision || !decisionForm.reason) return;
    try {
      const body: any = { decision: decisionForm.decision, reason: decisionForm.reason };
      if (decisionForm.decision === "APPROVED_WITH_CONDITIONS" && decisionForm.conditions) {
        body.conditions = decisionForm.conditions.split(";").map((s: string) => s.trim());
      }
      if (decisionForm.approvedAmount && (decisionForm.decision === "APPROVED" || decisionForm.decision === "APPROVED_WITH_CONDITIONS")) {
        body.approved_amount = parseFloat(decisionForm.approvedAmount);
      }
      await apiPost(`/decisions/${claimId}/decide`, body);
      setDecisionForm({ decision: "", reason: "", conditions: "", approvedAmount: "" });
      reloadWorkflow();
      // Reload claim data to show updated approved_amount
      apiGet(`/claims/${claimId}`).then((res) => setData(res.data)).catch(() => {});
    } catch (e: any) {
      alert("Failed: " + e.message);
    }
  };

  const handleFulfill = async (fulfilled: boolean) => {
    try {
      await apiPost(`/decisions/${claimId}/fulfill-conditions`, { fulfilled, evidence: "Verified by officer" });
      reloadWorkflow();
    } catch (e: any) {
      alert("Failed: " + e.message);
    }
  };

  const handleRespondClarification = async () => {
    if (!clarificationText) return;
    try {
      await apiPost(`/decisions/${claimId}/respond-clarification`, { content: clarificationText });
      setClarificationText("");
      reloadWorkflow();
    } catch (e: any) {
      alert("Failed: " + e.message);
    }
  };

  if (loading) return <p className="text-gray-500">Loading...</p>;
  if (!data) return <p className="text-red-500">Claim not found.</p>;

  const claim = data.claim;
  const lineItems = data.line_items || [];
  const documents = data.documents || [];

  return (
    <div className="max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/claims" className="text-blue-600 hover:underline text-sm">&larr; Back</Link>
        <h1 className="text-2xl font-bold text-gray-800">Claim Detail: {claim.CLAIM_ID}</h1>
      </div>

      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-500">Policy ID:</span> <strong>{claim.POLICY_ID}</strong></div>
          <div><span className="text-gray-500">Patient:</span> <strong>{claim.PATIENT_NAME}</strong> ({claim.PATIENT_ID})</div>
          <div><span className="text-gray-500">Provider:</span> <strong>{claim.NAMA_PROVIDER}</strong></div>
          <div><span className="text-gray-500">Service Type:</span> <strong>{claim.JENIS_LAYANAN}</strong></div>
          <div><span className="text-gray-500">Incident Date:</span> {claim.TANGGAL_KEJADIAN}</div>
          <div><span className="text-gray-500">Submission Date:</span> {claim.TANGGAL_PENGAJUAN}</div>
          <div><span className="text-gray-500">Diagnosis:</span> {claim.DIAGNOSIS_AWAL || "-"}</div>
          <div><span className="text-gray-500">Status:</span> <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">{claim.STATUS}</span></div>
          <div className="col-span-2 flex items-center gap-4">
            <div><span className="text-gray-500">Total Klaim:</span> <strong className="text-lg">Rp {claim.TOTAL_AMOUNT?.toLocaleString("id-ID")}</strong></div>
            {claim.APPROVED_AMOUNT != null && (
              <div><span className="text-gray-500">Disetujui:</span> <strong className="text-lg text-green-700">Rp {claim.APPROVED_AMOUNT?.toLocaleString("id-ID")}</strong>
                <span className="text-sm text-gray-500 ml-1">({((claim.APPROVED_AMOUNT / claim.TOTAL_AMOUNT) * 100).toFixed(0)}%)</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Line Items */}
      <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Procedures / Line Items</h2>
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="border p-2">#</th>
              <th className="border p-2 text-left">Description</th>
              <th className="border p-2">Code</th>
              <th className="border p-2 text-right">Cost (Rp)</th>
              <th className="border p-2">Notes</th>
            </tr>
          </thead>
          <tbody>
            {lineItems.map((item: any, i: number) => (
              <tr key={i}>
                <td className="border p-2 text-center">{item.ITEM_NO}</td>
                <td className="border p-2">{item.DESKRIPSI_TINDAKAN}</td>
                <td className="border p-2 text-center">{item.KODE_TINDAKAN || "-"}</td>
                <td className="border p-2 text-right">{item.JUMLAH_BIAYA?.toLocaleString("id-ID")}</td>
                <td className="border p-2">{item.CATATAN_TAMBAHAN || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Documents */}
      <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Documents</h2>
        {documents.length === 0 ? (
          <p className="text-gray-500 text-sm">No documents yet.</p>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc: any, i: number) => (
              <li key={i} className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded text-sm">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    doc.PARSE_STATUS === "PARSED" ? "bg-green-500" :
                    doc.PARSE_STATUS === "FAILED" ? "bg-red-500" :
                    "bg-gray-400"
                  }`}></span>
                  <span>{doc.FILE_NAME}</span>
                  {doc.DETECTED_DOC_TYPE && doc.DETECTED_DOC_TYPE !== "unknown" && (
                    <span className="px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded text-xs">{doc.DETECTED_DOC_TYPE}</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">{doc.DOCUMENT_TYPE}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    doc.PARSE_STATUS === "PARSED" ? "bg-green-100 text-green-700" :
                    doc.PARSE_STATUS === "FAILED" ? "bg-red-100 text-red-700" :
                    doc.PARSE_STATUS === "PENDING" ? "bg-yellow-100 text-yellow-700" :
                    "bg-gray-100 text-gray-500"
                  }`}>{doc.PARSE_STATUS || "N/A"}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Document Analysis */}
      <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-700">Document Analysis</h2>
          <button
            onClick={runAnalysis}
            disabled={analysisLoading}
            className="px-4 py-2 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 disabled:opacity-50"
          >
            {analysisLoading ? "Analyzing..." : analysis ? "Re-analyze" : "Document Analysis"}
          </button>
        </div>

        {analysis ? (
          <div>
            {/* Extracted Facts Summary */}
            {analysis.extraction?.extracted_data && (
              <div className="mb-4 p-4 bg-gray-50 rounded">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Clinical Facts (from documents)</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="text-gray-500">Pasien:</span> {analysis.extraction.extracted_data.patient_name}</div>
                  <div><span className="text-gray-500">RS:</span> {analysis.extraction.extracted_data.hospital}</div>
                  <div><span className="text-gray-500">Diagnosis:</span> {analysis.extraction.extracted_data.diagnosis_primary?.name} ({analysis.extraction.extracted_data.diagnosis_primary?.code})</div>
                  <div><span className="text-gray-500">Stay:</span> {analysis.extraction.extracted_data.length_of_stay_days} days</div>
                  <div><span className="text-gray-500">Total Biaya:</span> Rp {analysis.extraction.extracted_data.total_cost?.toLocaleString("id-ID")}</div>
                  <div><span className="text-gray-500">Dokter:</span> {analysis.extraction.extracted_data.attending_doctor}</div>
                </div>
                {analysis.extraction.extracted_data.clinical_findings && (
                  <p className="mt-2 text-xs text-gray-600"><span className="font-medium">Findings:</span> {analysis.extraction.extracted_data.clinical_findings}</p>
                )}
              </div>
            )}

            {/* Suggestions */}
            {analysis.suggestions && analysis.suggestions.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-600 mb-2">
                  Suggestions & Findings ({analysis.suggestions.length})
                </h3>
                <div className="space-y-2">
                  {analysis.suggestions.map((s: any, i: number) => (
                    <div
                      key={i}
                      className={`p-3 rounded border text-sm ${
                        s.suggestion_type === "flag" ? "bg-red-50 border-red-200" :
                        s.suggestion_type === "mismatch" ? "bg-yellow-50 border-yellow-200" :
                        "bg-blue-50 border-blue-200"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <span className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium mr-2 ${
                            s.suggestion_type === "flag" ? "bg-red-100 text-red-700" :
                            s.suggestion_type === "mismatch" ? "bg-yellow-100 text-yellow-700" :
                            "bg-blue-100 text-blue-700"
                          }`}>
                            {s.suggestion_type === "flag" ? "FLAG" : s.suggestion_type === "mismatch" ? "BEDA" : "INFO"}
                          </span>
                          <span className="font-medium">{s.field_name}</span>
                          <p className="mt-1 text-gray-700">{s.note}</p>
                          {s.form_value && s.form_value !== "-" && (
                            <p className="text-xs text-gray-500 mt-1">Form: <span className="line-through">{s.form_value}</span> | Documents: <strong>{s.extracted_value}</strong></p>
                          )}
                        </div>
                        {s.suggestion_id && !s.officer_decision && (
                          <div className="flex gap-1 ml-2">
                            <button
                              onClick={() => handleSuggestionDecision(s.suggestion_id, "accepted")}
                              className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs hover:bg-green-200"
                            >Accept</button>
                            <button
                              onClick={() => handleSuggestionDecision(s.suggestion_id, "rejected")}
                              className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs hover:bg-gray-200"
                            >Reject</button>
                          </div>
                        )}
                        {s.officer_decision && (
                          <span className={`px-2 py-1 rounded text-xs ${
                            s.officer_decision === "accepted" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                          }`}>
                            {s.officer_decision === "accepted" ? "Accepted" : "Rejected"}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysis.suggestions && analysis.suggestions.length === 0 && (
              <p className="text-green-600 text-sm">No discrepancies or findings require action.</p>
            )}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">Click the button above to analyze supporting documents for this claim.</p>
        )}
      </div>

      {/* Adjudication Result */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-700">Adjudication Result (Fuzzy AHP)</h2>
          <button
            onClick={runAdjudication}
            disabled={adjLoading}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {adjLoading ? "Processing..." : adjudication ? "Re-run Adjudikasi" : "Run Adjudikasi"}
          </button>
        </div>

        {adjudication ? (
          <div>
            {/* Score Gauge */}
            <div className="flex items-center gap-6 mb-6">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="12" />
                  <circle
                    cx="60" cy="60" r="50" fill="none"
                    stroke={adjudication.decision === "Auto-Approve" ? "#22c55e" : adjudication.decision === "Auto-Reject" ? "#ef4444" : "#f59e0b"}
                    strokeWidth="12"
                    strokeDasharray={`${(adjudication.final_score / 100) * 314} 314`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold">{adjudication.final_score}</span>
                </div>
              </div>
              <div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                  adjudication.decision === "Auto-Approve" ? "bg-green-100 text-green-700" :
                  adjudication.decision === "Auto-Reject" ? "bg-red-100 text-red-700" :
                  "bg-yellow-100 text-yellow-700"
                }`}>
                  {adjudication.decision}
                </span>
                <p className="text-sm text-gray-600 mt-2 max-w-md">{adjudication.decision_reason}</p>
              </div>
            </div>

            {/* Criteria Breakdown Table */}
            <h3 className="text-sm font-semibold text-gray-600 mb-2">Breakdown Kriteria</h3>
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="border p-2 text-left">Kriteria</th>
                  <th className="border p-2 text-center">Bobot</th>
                  <th className="border p-2 text-center">Label</th>
                  <th className="border p-2 text-center">TFN</th>
                  <th className="border p-2 text-center">Defuzzified</th>
                  <th className="border p-2 text-center">Kontribusi</th>
                  <th className="border p-2 text-left">Alasan</th>
                </tr>
              </thead>
              <tbody>
                {adjudication.criteria_breakdown?.map((c: any, i: number) => (
                  <tr key={i}>
                    <td className="border p-2 font-medium">{c.criteria_name}</td>
                    <td className="border p-2 text-center">{(c.weight * 100).toFixed(0)}%</td>
                    <td className="border p-2 text-center">
                      <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{c.linguistic_label}</span>
                    </td>
                    <td className="border p-2 text-center text-xs text-gray-500">({c.tfn?.join(", ")})</td>
                    <td className="border p-2 text-center">{c.defuzzified}</td>
                    <td className="border p-2 text-center font-semibold">{c.weighted_contribution}</td>
                    <td className="border p-2 text-gray-600 text-xs">{c.reason}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50 font-semibold">
                <tr>
                  <td className="border p-2" colSpan={5}>Total Score</td>
                  <td className="border p-2 text-center">{adjudication.final_score}</td>
                  <td className="border p-2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No adjudication result yet. Click the button above to run scoring.</p>
        )}
      </div>

      {/* Similar Claims (Cortex Search) */}
      {similarClaims.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mt-6">
          <h2 className="font-semibold text-gray-700 mb-3">
            Similar Claims <span className="text-xs font-normal text-indigo-500 ml-1">(Cortex Search)</span>
          </h2>
          <p className="text-xs text-gray-500 mb-3">Klaim historis dengan diagnosis/prosedur serupa — sebagai referensi keputusan.</p>
          <div className="space-y-2">
            {similarClaims.map((sc: any, i: number) => (
              <div key={i} className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded border">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{sc.claim_id}</span>
                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                      sc.status === "APPROVED" ? "bg-green-100 text-green-700" :
                      sc.status === "REJECTED" ? "bg-red-100 text-red-700" :
                      "bg-yellow-100 text-yellow-700"
                    }`}>{sc.status}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-0.5">{sc.diagnosis_awal} — {sc.jenis_layanan}</p>
                  <p className="text-xs text-gray-400">{sc.patient_name} | {sc.decision}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold">Rp {sc.total_amount?.toLocaleString("id-ID")}</p>
                  {sc.final_score && (
                    <p className={`text-xs font-medium ${
                      sc.final_score > 70 ? "text-green-600" : sc.final_score < 40 ? "text-red-600" : "text-yellow-600"
                    }`}>Score: {sc.final_score}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decision Workflow */}
      {workflow && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mt-6">
          <h2 className="font-semibold text-gray-700 mb-4">Decision & Workflow</h2>

          {/* Current Status */}
          <div className="mb-4">
            <span className="text-sm text-gray-500">Current Status: </span>
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
              workflow.current_status === "APPROVED" ? "bg-green-100 text-green-700" :
              workflow.current_status === "REJECTED" ? "bg-red-100 text-red-700" :
              workflow.current_status === "MANUAL_REVIEW" ? "bg-yellow-100 text-yellow-700" :
              workflow.current_status === "PENDING_CLARIFICATION" ? "bg-orange-100 text-orange-700" :
              workflow.current_status === "APPROVED_WITH_CONDITIONS" ? "bg-blue-100 text-blue-700" :
              "bg-gray-100 text-gray-700"
            }`}>
              {workflow.current_status}
            </span>
          </div>

          {/* Decision Panel - only show if MANUAL_REVIEW */}
          {workflow.current_status === "MANUAL_REVIEW" && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
              <h3 className="text-sm font-semibold text-yellow-800 mb-3">Make Decision</h3>
              <div className="space-y-3">
                <select
                  value={decisionForm.decision}
                  onChange={(e) => setDecisionForm({ ...decisionForm, decision: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                >
                  <option value="">-- Select Decision --</option>
                  <option value="APPROVED">Approve (Full)</option>
                  <option value="APPROVED_WITH_CONDITIONS">Approve with Conditions</option>
                  <option value="PENDING_CLARIFICATION">Pending Clarification</option>
                  <option value="REJECTED">Reject</option>
                </select>
                <textarea
                  placeholder="Alasan keputusan..."
                  value={decisionForm.reason}
                  onChange={(e) => setDecisionForm({ ...decisionForm, reason: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  rows={2}
                />
                {(decisionForm.decision === "APPROVED" || decisionForm.decision === "APPROVED_WITH_CONDITIONS") && (
                  <div>
                    <label className="text-xs text-gray-600 mb-1 block">Jumlah Disetujui (Rp)</label>
                    <input
                      type="number"
                      placeholder={claim.TOTAL_AMOUNT?.toString() || ""}
                      value={decisionForm.approvedAmount}
                      onChange={(e) => setDecisionForm({ ...decisionForm, approvedAmount: e.target.value })}
                      className="w-full border rounded px-3 py-2 text-sm"
                    />
                    {decisionForm.approvedAmount && claim.TOTAL_AMOUNT && (
                      <p className="text-xs text-gray-500 mt-1">
                        {((parseFloat(decisionForm.approvedAmount) / claim.TOTAL_AMOUNT) * 100).toFixed(1)}% dari total klaim
                      </p>
                    )}
                  </div>
                )}
                {decisionForm.decision === "APPROVED_WITH_CONDITIONS" && (
                  <input
                    type="text"
                    placeholder="Conditions (separate with ;)"
                    value={decisionForm.conditions}
                    onChange={(e) => setDecisionForm({ ...decisionForm, conditions: e.target.value })}
                    className="w-full border rounded px-3 py-2 text-sm"
                  />
                )}
                <button onClick={handleDecision} className="px-4 py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700">
                  Submit Decision
                </button>
              </div>
            </div>
          )}

          {/* Conditions Tracker */}
          {workflow.current_status === "APPROVED_WITH_CONDITIONS" && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
              <h3 className="text-sm font-semibold text-blue-800 mb-3">Verify Conditions</h3>
              {workflow.notes?.filter((n: any) => n.note_type === "condition" && n.status === "OPEN").map((n: any, i: number) => (
                <p key={i} className="text-sm text-blue-700 mb-1">- {n.content}</p>
              ))}
              <div className="flex gap-2 mt-3">
                <button onClick={() => handleFulfill(true)} className="px-3 py-1.5 bg-green-600 text-white text-xs rounded">
                  Conditions Met → Approve
                </button>
                <button onClick={() => handleFulfill(false)} className="px-3 py-1.5 bg-red-600 text-white text-xs rounded">
                  Conditions Not Met → Reject
                </button>
              </div>
            </div>
          )}

          {/* Clarification Response */}
          {workflow.current_status === "PENDING_CLARIFICATION" && (
            <div className="mb-6 p-4 bg-orange-50 border border-orange-200 rounded">
              <h3 className="text-sm font-semibold text-orange-800 mb-3">Respons Klarifikasi</h3>
              <textarea
                placeholder="Enter additional information/documents received..."
                value={clarificationText}
                onChange={(e) => setClarificationText(e.target.value)}
                className="w-full border rounded px-3 py-2 text-sm mb-2"
                rows={2}
              />
              <button onClick={handleRespondClarification} className="px-3 py-1.5 bg-orange-600 text-white text-xs rounded">
                Submit → Back to Review
              </button>
            </div>
          )}

          {/* Timeline */}
          {workflow.history && workflow.history.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">Timeline</h3>
              <div className="space-y-2 border-l-2 border-gray-200 pl-4">
                {workflow.history.map((h: any, i: number) => (
                  <div key={i} className="text-sm">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-indigo-500 -ml-5"></span>
                      <span className="font-medium">{h.old_status || "START"} → {h.new_status}</span>
                      <span className="text-xs text-gray-400">{h.changed_at?.slice(0, 16)}</span>
                    </div>
                    {h.reason && <p className="text-xs text-gray-500 ml-1">{h.reason}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          {workflow.notes && workflow.notes.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">Notes</h3>
              <div className="space-y-1">
                {workflow.notes.map((n: any, i: number) => (
                  <div key={i} className={`text-sm p-2 rounded ${n.status === "OPEN" ? "bg-yellow-50" : "bg-gray-50"}`}>
                    <span className="text-xs text-gray-400">[{n.note_type}]</span> {n.content}
                    {n.status === "RESOLVED" && <span className="text-xs text-green-600 ml-2">(resolved)</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
