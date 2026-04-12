import { globalIgnores } from "eslint/config";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";
import pluginVue from "eslint-plugin-vue";
import pluginVitest from "@vitest/eslint-plugin";
import testingLibrary from "eslint-plugin-testing-library";
import unocss from "@unocss/eslint-config/flat";
import { configs as wdioConfig } from "eslint-plugin-wdio";

export default defineConfigWithVueTs(
  {
    name: "src",
    files: ["**/*.{ts,mts,tsx,vue}"],
  },

  globalIgnores([
    "**/dist/**",
    "**/dist-ssr/**",
    "**/coverage/**",
    "src/volt/**",
    "src/gql/**",
    "src-tauri/target/**"
  ]),

  pluginVue.configs["flat/strongly-recommended"],
  vueTsConfigs.recommendedTypeChecked,
  {
    ...pluginVitest.configs.recommended,
    ...testingLibrary.configs["flat/vue"],
    files: ["src/**/__tests__/*"],
  },
  {
    ...wdioConfig['flat/recommended'],
    files: ["test/**"]
  },
  {
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
  {
    files: ["src/components/ui/**/*.vue"],
    rules: {
      "vue/require-default-prop": "off"
    }
  },
  unocss,
);
