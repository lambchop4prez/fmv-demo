// @ts-check
import antfu from '@antfu/eslint-config';

export default antfu(
  {
    unocss: true,
    formatters: true,
    pnpm: true,
    ignores: ['src/frontend/client'],
    stylistic: {
      overrides: {
        'style/semi': 'error',
      },
    },
  },
);
