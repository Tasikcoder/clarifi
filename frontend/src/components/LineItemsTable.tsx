"use client";

import { useState } from "react";

interface LineItem {
  item_no: number;
  deskripsi: string;
  kode: string;
  biaya: number;
  catatan: string;
}

interface Props {
  items: LineItem[];
  onChange: (items: LineItem[]) => void;
}

export default function LineItemsTable({ items, onChange }: Props) {
  const addRow = () => {
    onChange([
      ...items,
      { item_no: items.length + 1, deskripsi: "", kode: "", biaya: 0, catatan: "" },
    ]);
  };

  const removeRow = (index: number) => {
    const updated = items.filter((_, i) => i !== index).map((item, i) => ({ ...item, item_no: i + 1 }));
    onChange(updated);
  };

  const updateRow = (index: number, field: keyof LineItem, value: string | number) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  };

  const total = items.reduce((sum, item) => sum + (item.biaya || 0), 0);

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-gray-700">Procedures / Cost Breakdown</h3>
        <button
          type="button"
          onClick={addRow}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
        >
          + Add Item
        </button>
      </div>

      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2 w-12">#</th>
            <th className="border p-2">Procedure Description</th>
            <th className="border p-2 w-32">Code (CPT/ICD)</th>
            <th className="border p-2 w-40">Amount (Rp)</th>
            <th className="border p-2">Notes</th>
            <th className="border p-2 w-16"></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, index) => (
            <tr key={index}>
              <td className="border p-2 text-center">{item.item_no}</td>
              <td className="border p-1">
                <input
                  type="text"
                  value={item.deskripsi}
                  onChange={(e) => updateRow(index, "deskripsi", e.target.value)}
                  className="w-full px-2 py-1 border rounded"
                  placeholder="Appendectomy, dll"
                />
              </td>
              <td className="border p-1">
                <input
                  type="text"
                  value={item.kode}
                  onChange={(e) => updateRow(index, "kode", e.target.value)}
                  className="w-full px-2 py-1 border rounded"
                  placeholder="44950"
                />
              </td>
              <td className="border p-1">
                <input
                  type="number"
                  value={item.biaya || ""}
                  onChange={(e) => updateRow(index, "biaya", parseFloat(e.target.value) || 0)}
                  className="w-full px-2 py-1 border rounded text-right"
                  placeholder="0"
                />
              </td>
              <td className="border p-1">
                <input
                  type="text"
                  value={item.catatan}
                  onChange={(e) => updateRow(index, "catatan", e.target.value)}
                  className="w-full px-2 py-1 border rounded"
                />
              </td>
              <td className="border p-1 text-center">
                <button
                  type="button"
                  onClick={() => removeRow(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  X
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="bg-gray-50 font-semibold">
            <td colSpan={3} className="border p-2 text-right">Total:</td>
            <td className="border p-2 text-right">
              {total.toLocaleString("id-ID")}
            </td>
            <td colSpan={2} className="border p-2"></td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
