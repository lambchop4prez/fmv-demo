from celery import Celery
from config import BrokerSettings, MongoSettings
from handlers import RobotHandlers

mongo_settings = MongoSettings()
broker_settings = BrokerSettings()
worker = Celery(
    __name__,
    broker=broker_settings.url,
    backend="workers.Backend",
    task_track_started=True,
    mongodb_backend_settings={
        "host": mongo_settings.HOST,
        "database": mongo_settings.DATABASE,
        "taskmeta_collection": "tasks",
    },
)

#
# @before_task_publish.connect
# def on_task_publish(headers=None, body=None, exchange=None, routing_key=None, **kwargs):
#     task_id = headers.get("id")
#
#     robot, _, _ = body
#
#     worker.backend.collection.insert_one(
#         {
#             "_id": task_id,
#             "status": "QUEUED",
#             "result": None,
#             "traceback": None,
#             "children": None,
#             "robot": robot,
#         }
#     )


@worker.task
def primes(robot: str, count: int) -> None:
    RobotHandlers(robot).primes(count)
