import { defineConfig } from "cypress";
import vitePreprocessor from 'cypress-vite';

interface RobotProfile {
  name: string;
  is_great: boolean;
  description: string;
  location: string;
}
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
      on('before:run', (/*details*/) => {
        cy.fixture('seed').then((data: Array<RobotProfile>) => {
          data.forEach((element: RobotProfile) => {
            cy.task('httpRequest', {
              url: 'http://localhost:8000/v1/robot/',
              body: element
            });
          });
        });
      });
    },
  },
});
