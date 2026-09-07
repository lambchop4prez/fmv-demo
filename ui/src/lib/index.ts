import type { paths } from "~/client/api";
import createClient from "openapi-fetch";

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

// credentials: 'include' so the HttpOnly session cookie is sent cross-origin (D1=a).
const client = createClient<paths>({
  baseUrl: apiEndpoint || "http://localhost:8000/api/v1",
  credentials: "include",
});
export default client;
