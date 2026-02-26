from typing import Any, Mapping, Optional

from celery.backends.mongodb import MongoBackend


class Backend(MongoBackend):
    def _store_result(
        self,
        task_id: str,
        result: Mapping,
        state: Mapping,
        traceback: Optional[str] = None,
        request: Optional[Mapping] = None,
        **kwargs: dict[str, Any],
    ) -> Any:
        task_info = self._get_result_meta(  # type: ignore
            result=self.encode(result),
            state=state,
            traceback=traceback,
            request=request,
            format_date=False,
        )
        task_info["task_id"] = task_id
        if request is not None and getattr(request, "args", None):
            robot = request.args[0]
        else:
            robot = "unknown"

        self.collection.update_one(
            {"name": robot, "tasks.task_id": task_id},
            {"$set": {"tasks.$": task_info}},
        )
        return task_info
