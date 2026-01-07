from config.mongo import settings

CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": settings.HOST,
    "port": 27017,
    "database": settings.DATABASE,
    "taskmeta_collection": "RobotTaskDocument",
}
