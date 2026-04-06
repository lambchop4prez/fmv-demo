import type { UserModule } from '~/types';

// https://github.com/antfu/vite-plugin-pwa#automatic-reload-when-new-content-available
export const install: UserModule = ({ router }) => {
  if (import.meta.env.SSR)
    return;

  router.isReady()
    .then(async () => {
      const { registerSW } = await import('virtual:pwa-register');
      registerSW({ immediate: true });
    })
    .catch(() => { });
};
