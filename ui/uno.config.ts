import {
  createLocalFontProcessor,
} from '@unocss/preset-web-fonts/local';
import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetTypography,
  presetWebFonts,
  presetWind4,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss';
import presetAnimations from 'unocss-preset-animations';
import { presetShadcn } from 'unocss-preset-shadcn';

export default defineConfig({
  shortcuts: [
    // ['icon-btn', 'inline-block cursor-pointer select-none opacity-75 transition duration-200 ease-in-out hover:opacity-100 hover:text-purple-600'],
    // ['card', 'm-auto block max-w-md rounded border-solid bg-light-700 p-6 shadow-sm dark:bg-dark-700'],
    // ['label-input', 'mb-2.5 block text-align-left text-sm font-medium'],
    // ['label-checkbox', 'ms-2 mb-2.5 select-none text-align-left text-sm font-medium'],
    // ['input-text', 'mb-2.5 block  w-full rounded border-solid px-3 py-2.5 text-sm dark:bg-dark'],
    // ['input-checkbox', 'h-4 w-4 mb-2.5 rounded border-solid text-align-left']
  ],
  presets: [
    presetWind4({
      preflights: {
        reset: true,
      },
    }),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
    }),
    presetTypography(),
    presetWebFonts({
      fonts: {
        sans: 'DM Sans',
        serif: 'DM Serif Display',
        mono: 'DM Mono',
      },
      processors: createLocalFontProcessor(),
    }),
    presetAnimations(),
    presetShadcn({
      color: "violet"
      // color: {
      //   base: "gray",
      //   dark: {
      //     primary: "0.71 0.13% 215%", // cyan-500
      //     "primary-foreground": "0.30 0.05% 230%",
      //     "card-foreground": "0.985 0.002% 247.839%"
      //   },
      //   light: {
      //     primary: "0.61 0.11% 222%",
      //     "primary-foreground": "0.98 0.02% 201%"
      //   }
      // }
    })
  ],
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
  ],
  safelist: 'prose prose-sm m-auto text-left'.split(' '),
  content: {
    pipeline: {
      include: [
        // the default
        /\.(vue|svelte|[jt]sx|mdx?|astro|elm|php|phtml|html)($|\?)/,
        // include js/ts files
        "(components|src)/**/*.{js,ts}",
      ],
    },
  },
});
