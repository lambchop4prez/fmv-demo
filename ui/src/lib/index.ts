import type { paths } from "~/client/api";
import createClient, { Middleware } from "openapi-fetch";
import { useCookies } from '@vueuse/integrations/useCookies'


const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
const publicEndpoints = ["/auth/pocketid/login", "/auth/pocketid/logout"]
const authMiddleware: Middleware = {
  onRequest({ schemaPath, request }) {
    if (publicEndpoints.some((pathName => schemaPath.startsWith(pathName)))) {
      return undefined;
    }
    const cookies = useCookies()
    console.log(cookies.getAll())
    console.log(window.document.cookie)
    request.headers.set("Cookie", `session=${cookies.get("session")}`)
  }
}

const client = createClient<paths>({ baseUrl: apiEndpoint || "http://localhost:8000/api/v1" });
client.use(authMiddleware)
export default client;
