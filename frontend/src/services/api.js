
// Flask API address.
// The Vite dev server proxies /api to the Flask backend
// (see vite.config.js), so the frontend and API share an
// origin. Session cookies therefore work the same whether
// the site is opened via localhost or 127.0.0.1.
export const API_BASE_URL = "";

// Turn a relative upload path such as "covers/x.jpg" into
// a URL the browser can load from the Flask backend.
export function mediaUrl(path) {

  if (!path) {
    return null;
  }

  if (
    /^(?:https?:)?\/\//i.test(path)
    || path.startsWith("data:")
    || path.startsWith("blob:")
  ) {
    return path;
  }

  return `${API_BASE_URL}/api/media/${path.replace(/^\/+/, "")}`;
}

// Reusable function for communicating with Flask.
export async function apiRequest(path, options = {}) {

  // Prepare request headers.
  const headers = {
    ...options.headers
  };

  // JSON requests need the Content-Type header.
  // FormData uploads must keep the browser-generated boundary.
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // Send request to Flask.
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,

      // Important: allow the browser to send and receive
      // Flask authentication session cookies.
      credentials: "include"
    });

  } catch (error) {

    // The browser could not reach the backend at all
    // (for example it has not been started yet).
    throw new Error(
      "Could not reach the server. Make sure the Flask backend is running on port 5000, then try again."
    );
  }

  // Convert the response into JSON.
  const data = await response.json().catch(() => ({}));

  // Handle unsuccessful responses.
  if (!response.ok) {
    throw new Error(
      data.message || `Request failed: ${response.status}`
    );
  }

  return data;
}
