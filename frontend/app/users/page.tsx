"use client";

import { useEffect, useState } from "react";
import { fetchUsers } from "../../services/api";

export default function UsersPage() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      const data = await fetchUsers();
      setUsers(data);
    } catch (error) {
      console.error("Error loading users:", error);
    }
  }

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">User List</h1>
      <ul className="space-y-2">
        {users.map((user: { id: number; name: string; email: string }) => (
          <li key={user.id} className="border p-2 rounded">
            {user.name} ({user.email})
          </li>
        ))}
      </ul>
    </div>
  );
}