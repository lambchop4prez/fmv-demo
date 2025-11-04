import { globalIgnores } from "eslint/config";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";
import pluginVue from "eslint-plugin-vue";
import pluginVitest from "@vitest/eslint-plugin";
import pluginPlaywright from "eslint-plugin-playwright";
import unocss from "@unocss/eslint-config/flat";

export default defineConfigWithVueTs(
  {
    name: "src/frontend",
    files: ["**/*.{ts,mts,tsx,vue}"],
  },

  globalIgnores([
    "**/dist/**",
    "**/dist-ssr/**",
    "**/coverage/**",
    "src/volt/**",
    "src/gql/**",
  ]),

  pluginVue.configs["flat/strongly-recommended"],
  vueTsConfigs.recommendedTypeChecked,
  {
    ...pluginVitest.configs.recommended,
    files: ["src/**/__tests__/*"],
  },

  {
    ...pluginPlaywright.configs["flat/recommended"],
    files: ["e2e/**/*.{test,spec}.{js,ts,jsx,tsx}"],
  },
  {
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
  unocss,
);
