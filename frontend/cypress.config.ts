import { defineConfig } from "cypress";
import vitePreprocessor from 'cypress-vite';

export default defineConfig({
  downloadsFolder: 'test/downloads',
  fixturesFolder: 'test/fixtures',
  screenshotsFolder: 'test/screenshots',
  videosFolder: 'test/videos',
  e2e: {
    baseUrl: 'http://localhost:8080/',
    specPattern: 'test/e2e/**/*.spec.*',
    supportFile: 'test/support/e2e.ts',
    setupNodeEvents(on/*, config*/) {
      // implement node event listeners here
      on('file:preprocessor', vitePreprocessor());

    },
  },
});
