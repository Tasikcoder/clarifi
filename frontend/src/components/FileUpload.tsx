"use client";

import { useRef, useState } from "react";

interface Props {
  files: File[];
  onChange: (files: File[]) => void;
}

export default function FileUpload({ files, onChange }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = (newFiles: FileList | null) => {
    if (!newFiles) return;
    onChange([...files, ...Array.from(newFiles)]);
  };

  const removeFile = (index: number) => {
    onChange(files.filter((_, i) => i !== index));
  };

  return (
    <div>
      <h3 className="font-semibold text-gray-700 mb-2">Supporting Documents</h3>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
          dragOver ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
        }`}
      >
        <p className="text-gray-500">
          Drag & drop files here, or <span className="text-blue-600 underline">click to browse</span>
        </p>
        <p className="text-xs text-gray-400 mt-1">PDF, JPG, PNG, DOCX (Medical Report, Invoice, Claim Form)</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png,.docx"
        onChange={(e) => handleFiles(e.target.files)}
        className="hidden"
      />

      {files.length > 0 && (
        <ul className="mt-3 space-y-1">
          {files.map((file, index) => {
            const ext = file.name.split(".").pop()?.toLowerCase() || "";
            const icon = ext === "pdf" ? "PDF" : ext === "docx" ? "DOC" : ext === "png" || ext === "jpg" || ext === "jpeg" ? "IMG" : "FILE";
            const iconColor = ext === "pdf" ? "bg-red-100 text-red-700" : ext === "docx" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600";
            return (
              <li key={index} className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${iconColor}`}>{icon}</span>
                  <span className="text-sm text-gray-700">{file.name} ({(file.size / 1024).toFixed(0)} KB)</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="text-red-500 text-sm hover:text-red-700"
                >
                  Remove
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
