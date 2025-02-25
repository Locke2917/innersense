const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchUsers() {
  const response = await fetch(`${API_URL}/users/`);
  console.log(response)
  if (!response.ok) throw new Error("Failed to fetch users");
  return response.json();
}

export async function fetchUser(userId) {
  const response = await fetch(`${API_URL}/users/${userId}`);
  console.log(response)
  if (!response.ok) throw new Error("Failed to fetch users");
  return response.json();
}

export async function createUser(user) {
  const response = await fetch(`${API_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(user),
  });
  if (!response.ok) throw new Error("Failed to create user");
  return response.json();
}

export async function deleteUser(userId) {
  const response = await fetch(`${API_URL}/users/${userId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete user");
  return response.json();
}