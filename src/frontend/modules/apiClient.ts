import type { UserModule } from '~/types';
import { client } from '~/client/client.gen';

export const install: UserModule = (_) => {
  const endpoint = import.meta.env.FRONTEND_API_BASE_URL || 'http://localhost:8000';
  client.setConfig({
    baseUrl: endpoint,
  });
};
