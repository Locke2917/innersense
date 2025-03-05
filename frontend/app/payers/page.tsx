"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchPayers } from "../../services/api";

export default function PayersPage() {
  const [payers, setPayers] = useState([]);
  const router = useRouter();

  useEffect(() => {
    loadPayers();
  }, []);

  async function loadPayers() {
    try {
      const data = await fetchPayers();
      setPayers(data);
    } catch (error) {
      console.error("Error loading payers:", error);
    }
  }

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Select a Payer</h1>
      <ul className="space-y-2">
        {payers.map((payer: { id: string; name: string }) => (
          <li
            key={payer.id}
            className="border p-2 rounded cursor-pointer hover:bg-gray-100"
            onClick={() => router.push(`/payers/${payer.id}`)}
          >
            {payer.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
