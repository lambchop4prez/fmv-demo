import {
  createLocalFontProcessor,
} from '@unocss/preset-web-fonts/local';
import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetTypography,
  presetUno,
  presetWebFonts,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss';

export default defineConfig({
  shortcuts: [
    ['btn', 'px-4 py-1 rounded inline-block bg-teal-700 text-white cursor-pointer !outline-none hover:bg-teal-800 disabled:cursor-default disabled:bg-gray-600 disabled:opacity-50'],
    ['icon-btn', 'inline-block cursor-pointer select-none opacity-75 transition duration-200 ease-in-out hover:opacity-100 hover:text-teal-600'],
    ['card', 'm-auto block max-w-md rounded border-solid bg-light-700 p-6 shadow-sm dark:bg-dark-700'],
    ['label-input', 'mb-2.5 block text-align-left text-sm font-medium'],
    ['label-checkbox', 'ms-2 mb-2.5 select-none text-align-left text-sm font-medium'],
    ['input-text', 'mb-2.5 block  w-full rounded border-solid px-3 py-2.5 text-sm dark:bg-dark'],
    ['input-checkbox', 'h-4 w-4 mb-2.5 rounded border-solid text-align-left']
  ],
  presets: [
    presetUno(),
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
  ],
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
  ],
  safelist: 'prose prose-sm m-auto text-left'.split(' '),
});
