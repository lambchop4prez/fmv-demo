import type { paths } from "~/client/api";
import createClient from "openapi-fetch";

const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

const client = createClient<paths>({baseUrl: apiEndpoint || "http://localhost:8000"});
export default client;
