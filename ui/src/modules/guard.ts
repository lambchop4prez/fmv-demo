import type { UserModule } from '~/types';

export const install: UserModule = ({ router }) => {
  router.beforeEach((to, _, next) => {
    const { isAuthenticated } = useUserStore();
    if (!to.meta.public && !isAuthenticated) {
      next({ name: "/login" })
    }
    else {
      next();
    }
  });
};
