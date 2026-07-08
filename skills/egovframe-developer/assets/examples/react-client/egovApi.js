export async function requestJson(path, options = {}) {
  const response = await fetch(`${import.meta.env.VITE_EGOV_API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    credentials: "include",
    ...options,
  });

  if (!response.ok) {
    throw new Error(`eGovFrame API request failed: ${response.status}`);
  }

  return response.json();
}

export function getNotices() {
  return requestJson("/api/notices");
}
