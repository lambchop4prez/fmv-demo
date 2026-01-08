# FMV Backend

This directory contains the backend code which consists of an api
and collection of asynchronous workers.

## Tooling

- [FastAPI](https://fastapi.tiangolo.com) Modern asynchronous Python API server. Provides OpenAPI support out of the box and can integrate with WebSockets, GraphQL, and task queues.
- [uv](https://docs.astral.sh/uv/) Python package manager, managing projects with `pyproject.toml`
- [Pydantic](https://pydantic.dev) Python typing system. Used by FastAPI to generate OpenAPI schema
- [Celery](https://docs.celeryq.dev/en/stable/) - A simple distributed task queue. This is used to create asynchronous workers.

### Infrastructure

- [MongoDB](https://www.mongodb.com) - Backing data store for application state and worker state
- [RabbitMQ](https://www.rabbitmq.com) - Broker for sending messages from api to workers

## Layout

Below is a tree of this project with descriptions for major directories/files.

```
.
├── pkg
│   ├── config/                     Configuration models
│   ├── handlers/                   Task handlers, called by workers
│   ├── models/                     Pydantic models
│   ├── repository/                 Data access API
│   ├── repository_inmemory/        Data access implementation stub
│   ├── repository_mongodb/         Data access implementation via MongoDB
│   ├── service/                    Service layer, to be injected into FastAPI
│   └── workers/                    Celery worker setup
├── src
│   └── api
│       ├── dependencies            FastAPI Dependencies
│       │   └── [...].py
│       ├── v1                      API Versioning
│       │   ├── endpoints           API Endpoints
│       │   │   ├── __init__.py
│       │   │   └── robot.py
│       │   ├── __init__.py
│       │   └── router.py           API Router, composed of endpoints
│       ├── __init__.py
│       ├── main.py                 API entrypoint
│       └── util.py
├── Dockerfile
├── mod.just                        `just` module defining frontend tasks
├── pyproject.toml                  Python project configuration using `uv`
├── README.md                       :round_pushpin: You are here
└── uv.lock                         Lock file for reproducible builds
```
