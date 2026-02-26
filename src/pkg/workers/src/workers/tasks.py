from typing import Any, Mapping, cast

from celery import Celery
from celery.signals import before_task_publish
from config import BrokerSettings, MongoSettings
from handlers import RobotHandlers

from . import Backend

mongo_settings = MongoSettings()
broker_settings = BrokerSettings()
worker = Celery(
    __name__,
    broker=broker_settings.url,
    backend="workers.Backend",
    task_track_started=True,
)
worker.config_from_object("workers.task_config")


@before_task_publish.connect
def on_task_publish(headers: Mapping, body: Mapping, **kwargs: dict[str, Any]) -> None:
    task_id = headers.get("id")

    args, _, _ = body
    filter = {"name": args[0]}
    value = {
        "$push": {
            "tasks": {
                "task_id": task_id,
                "status": "QUEUED",
                "result": None,
                "traceback": None,
                "children": None,
                "robot": args[0],
            }
        },
    }

    cast(Backend, worker.backend).collection.update_one(
        filter,
        value,
        upsert=True,
    )


@worker.task
def primes(robot: str, count: int) -> None:
    RobotHandlers(robot).primes(count)
