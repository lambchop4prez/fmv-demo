# FMV Frontend

This is a simple Vue-based frontend based on the existing [Vitesse](https://github.com/antfu-collective/vitesse) project

## Tooling

- [Vue](https://vuejs.org/) Progressive javascript framework. Reactive, composable, strongly typed.
- [Vite](https://vite.dev/) Frontend build tool. _Much_ faster than webpack.
- [Vitesse](https://github.com/antfu-collective/vitesse) Opinionated starter template. Provides a reasonable starting point.
- [UnoCSS](https://github.com/unocss/unocss) On-demand atomic CSS engine. Similar to Tailwind in that you can use class-based styling utilities (i.e. no manual css)
- [`@hey-api/openapi-ts`](https://github.com/hey-api/openapi-ts) Generate client SDK from OpenAPI spec

## Layout

Below is a tree of this project with descriptions for major directories/files.

```
.
├── locales                             Frontend localization strings
│   ├── ...
│   ├── en.yml
│   ├── ...
├── public                              Static public assets (images/etc)
│   ├── assets
│   └── ...
├── src
│   ├── client
│   │   └── api.d.ts                    Auto-generated types for the API
│   ├── components                      Vue Components collection
│   │   ├── __test__                    Inline Unit Tests
│   │   │   └── RobotItem.test.ts
│   │   ├── README.md                   Markdown components
│   │   ├── RobotItem.vue
│   │   └── [...].vue
│   ├── composables                     Composables for reusable operations
│   │   ├── dark.ts
│   │   └── robotList.ts
│   ├── layouts                         Router-based layouts. Used by pages
│   │   ├── default.vue                 Standard Vue components
│   │   ├── [...].vue
│   │   └── README.md                   Markdown Vue components
│   ├── lib
│   │   └── index.ts                    Generated API Client
│   ├── modules                         User modules installed at app startup
│   │   └── [...].ts
│   ├── pages                           Page-based router. Routes reflect this directory.
│   │   ├── hi
│   │   │   └── [name].vue
│   │   ├── robot
│   │   │   └── index.vue
│   │   ├── [...all].vue
│   │   ├── about.md                    Markdown Vue components
│   │   ├── index.vue                   Root Vue component
│   │   └── README.md
│   ├── stores                          State storage using pinia
│   │   ├── robotProfile.ts
│   │   └── user.ts
│   ├── styles                          Stylesheets
│   │   └── [...].css
│   ├── App.vue                         Root Vue component
│   ├── auto-imports.d.ts
│   ├── components.d.ts
│   ├── main.ts                         Vue entrypoint
│   ├── shims.d.ts
│   ├── typed-router.d.ts
│   └── types.ts
├── Dockerfile
├── eslint.config.ts
├── index.html                          HTML root, bootstraps Vue via src/main.ts
├── mod.just                            `just` module defining frontend tasks
├── package.json
├── pnpm-lock.yaml                      Lock file for reproducible builds
├── pnpm-workspace.yaml
├── README.md                           :round_pushpin: You are here
├── tsconfig.json
├── uno.config.ts                       UnoCSS config
├── vite.config.ts                      Build system configuration
├── vitest.config.ts
└── vitest.setup.ts                     Script that runs before unit tests
```
