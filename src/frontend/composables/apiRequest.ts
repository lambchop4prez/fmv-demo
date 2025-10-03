import { createFetch } from '@vueuse/core';

export const useApiRequest = createFetch({
  baseUrl: `https://${import.meta.env.VITE_API_ENDPOINT}/api/${import.meta.env.VITE_API_VERSION}`,

});
