from config.mongo import settings

result_backend = "mongodb"
mongodb_backend_settings = {
    "host": settings.HOST,
    "port": 27017,
    "database": settings.DATABASE,
    "taskmeta_collection": "RobotTaskDocument",
}
