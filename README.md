# Demo project using FastAPI, MongoDB, and Vue

:construction: :hammer: **Under Construction** :wrench: :construction:

## Tooling

### Backend

- [FastAPI](https://fastapi.tiangolo.com) Modern asynchronous Python API server. Provides OpenAPI support out of the box and can integrate with WebSockets, GraphQL, and task queues.
- [uv](https://docs.astral.sh/uv/) Python package manager
- [Pydantic](https://pydantic.dev) Python typing system. Used by FastAPI to generate OpenAPI schema

### Frontend

- [Vue](https://vuejs.org/) Progressive javascript framework. Reactive, composable, strongly typed.
- [Vite](https://vite.dev/) Frontend build tool. _Much_ faster than webpack.
- [Vitesse](https://github.com/antfu-collective/vitesse) Opinionated starter template. Provides a reasonable starting point.
- [UnoCSS](https://github.com/unocss/unocss) On-demand atomic CSS engine. Similar to Tailwind in that you can use class-based styling utilities (i.e. no manual css)

### Integrations/Shared

- [Docker](https://www.docker.com/) - Containerization platform
- [`@hey-api/openapi-ts`](https://github.com/hey-api/openapi-ts) - Generate client SDK from OpenAPI spec
- [`pre-commit`](https://pre-commit.com/) - Automatic linting/formatting at commit time

## Layout

```
.
├── locales                                 Frontend localization strings
│   ├── ...
│   ├── en.yml
│   └── ...
├── src
│   ├── api                                 FastAPI api
│   │   ├── config                          Application configuration model definitions
│   │   │   ├── mongo_settings.py
│   │   │   └── settings.py
│   │   ├── dependencies                    FastAPI Dependency declarations
│   │   ├── main.py                         API Entrypoint
│   │   └── v1                              API v1 Routes
│   │       ├── endpoints
│   │       └── router.py
│   ├── frontend                            Vue frontend
│   │   ├── App.vue                         Root Vue component
│   │   ├── components                      Vue component collection
│   │   ├── composables                     Vue composables for reusable operations
│   │   ├── layouts                         Router-based layouts. Used by pages
│   │   ├── main.ts
│   │   ├── modules                         User modules installed at app startup
│   │   ├── pages                           Page-based router. Routes reflect this directory.
│   │   ├── stores                          State storage using pinia
│   │   └── styles
│   └── pkg                                 API library modules
│       ├── models                          API Models (pydantic models)
│       ├── repository                      Data access API using `Protocol` and `abstractmethod`
│       ├── repository_inmemory             In memory implementation of data access API
│       ├── repository_mongodb              MongoDB implementation of data access API
│       └── service                         Service layer, injected into FastAPI and consuming data access API
├── test
│   ├── api                                 API Tests
│   └── frontend                            Frontend component tests
├── docker-compose.yaml                     Docker compose file to build/deploy the entire stack
├── Dockerfile.backend                      Backend (API) Dockerfile
├── Dockerfile.frontend                     Frontend Dockerfile
├── eslint.config.js
├── index.html                              Frontend root, bootstraps Vue app
├── openapi-ts.config.ts                    OpenAPI client generator config
├── package.json                            Node package and project configuration using `pnpm`
├── pnpm-lock.yaml                          Lock file for reproducible frontend builds
├── pnpm-workspace.yaml                     Pnpm workspace configuration
├── public                                  Static assets (fonts, images, etc)
├── pyproject.toml                          Python project configuration using `uv`
├── README.md                               This file, you are here :round_pushpin:
├── tsconfig.json                           Typescript compiler config
├── uno.config.ts                           Unocss config
├── uv.lock                                 Lock file for reproducible backend builds
└── vite.config.ts                          Frontend build configuration
```

## To Do

- [x] - In memory database stub
- [x] - mongodb database adapter
- [ ] - API Authentication (OAuth2)
- [ ] - Complete docker-compose file
- [ ] - Unit/E2E testing

## Reference

- <https://github.com/mongodb-developer/mongodb-pymongo-fastapi>
- <https://github.com/mongodb-labs/full-stack-fastapi-mongodb>
- <https://github.com/antfu-collective/vitesse>
