from celery.backends.mongodb import MongoBackend


class Backend(MongoBackend):
    def _store_result(
        self, task_id, result, state, traceback=None, request=None, **kwargs
    ):
        task_info = self._get_result_meta(
            result=self.encode(result),
            state=state,
            traceback=traceback,
            request=request,
            format_date=False,
        )
        task_info["id"] = task_id
        self.collection.update_one({"_id": task_id}, {"$set": task_info}, upsert=True)
        return super()._store_result(
            task_id, result, state, traceback, request, **kwargs
        )
