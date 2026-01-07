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

    robot, _, _ = body

    # await RobotTaskDocument(robot=robot[0], task_id=task_id, status="QUEUED").insert()

    cast(Backend, worker.backend).collection.insert_one(
        {
            "task_id": task_id,
            "status": "QUEUED",
            "result": None,
            "traceback": None,
            "children": None,
            "robot": robot[0],
        }
    )


@worker.task
def primes(robot: str, count: int) -> None:
    RobotHandlers(robot).primes(count)
