from celery.backends.mongodb import MongoBackend
from celery.result import ResultSet


class Backend(MongoBackend):
    def _store_result(
        self, task_id, result, state, traceback=None, request=None, **kwargs
    ) -> ResultSet:
        task_info = self._get_result_meta(
            result=self.encode(result),
            state=state,
            traceback=traceback,
            request=request,
            format_date=False,
        )
        task_info["task_id"] = task_id
        self.collection.update_one(
            {"task_id": task_id}, {"$set": task_info}, upsert=True
        )
        return task_info
