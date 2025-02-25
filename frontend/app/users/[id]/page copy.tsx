"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchUser } from "../../../services/api";

export default function UserRecord() {
  const { id } = useParams();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      const data = await fetchUser(id);
      setUser(data);
    } catch (error) {
      console.error("Error loading users:", error);
    }
  }
  if (!user) return <p>Loading...</p>;

  return (
    <div className="bg-white p-6 shadow-lg rounded-lg">
      <h2 className="text-xl font-bold text-gray-800">{user.name}</h2>
      <p className="text-gray-600">Email: {user.email}</p>
      <p className="text-gray-600">Phone: {user.phone}</p>
    </div>
  );
}
