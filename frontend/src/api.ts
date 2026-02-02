const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// 🟢 LOGIN
export async function login(username: string, password: string) {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);
  body.set("grant_type", "password");

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!res.ok) throw new Error("Invalid credentials");
  return res.json(); // returns { access_token: "..." }
}

// 🟢 FORECAST (Protected route)
export async function forecast(token: string, file: File, horizon: number) {
  const form = new FormData();
  form.append("file", file);
  form.append("horizon", String(horizon));

  const res = await fetch(`${API_BASE}/forecast`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: form,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// 🟢 DOWNLOAD CSV (Protected route)
export async function downloadCsv(token: string, file: File, horizon: number) {
  const form = new FormData();
  form.append("file", file);
  form.append("horizon", String(horizon));

  const res = await fetch(`${API_BASE}/download`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: form,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.blob();
}

// 🟢 ALERTS (Protected route)
export async function getAlerts(token: string) {
  const res = await fetch(`${API_BASE}/alerts`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// 🟢 REPORT (Protected route)
export async function getReport(token: string) {
  const res = await fetch(`${API_BASE}/report`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// 🟢 CREATE USER (Protected route)
export async function createUser(
  token: string,
  payload: { email: string; name: string; password: string }
) {
  const res = await fetch(`${API_BASE}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
