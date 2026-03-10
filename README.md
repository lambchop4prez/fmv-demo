# Demo project using FastAPI, MongoDB, and Vue

:construction: :hammer: **Under Construction** :wrench: :construction:

## Tooling

- [`mise`](https://mise.jdx.dev) Manages the dev environment
- [`just`](https://just.systems) Just a task runner
- [Docker](https://www.docker.com/) Containerization platform

To get started, make sure to have `mise` (and docker) installed, clone the repo and run `mise install`. That will install everything needed to run this project (except Docker).

`just` is used as a task runner, you can see the available tasks by running `just --list`

## Development

To get started developing, first load up the backing infrastructure with `just infra`. Then, start up all the dev servers locally with `just dev`. Simple as that.

When done, `<Ctrl>c` to stop the dev servers and `just infra-down` to teardown the infrastructure

### OAuth2

When using OAuth2, a JWT secret is needed. One can be generated using the following command:

```sh
echo "BACKEND_JWT_SECRET=$(openssl rand -base64 32 | tr -- '+/' '-_')" > .secrets.env
```



## To Do

- [x] - In memory database stub
- [x] - mongodb database adapter
- [ ] - API Authentication (OAuth2)
- [x] - Complete docker-compose file
- [x] - Unit/E2E testing

## Reference

- <https://github.com/mongodb-developer/mongodb-pymongo-fastapi>
- <https://github.com/mongodb-labs/full-stack-fastapi-mongodb>
- <https://github.com/antfu-collective/vitesse>
