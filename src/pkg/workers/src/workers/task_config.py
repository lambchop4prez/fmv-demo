from config.mongo import get_mongo_settings

mongo_settings = get_mongo_settings()

result_backend = "mongodb"
mongodb_backend_settings = {
    "host": mongo_settings.HOST,
    "port": 27017,
    "database": mongo_settings.DATABASE,
    "taskmeta_collection": "RobotDocument",
}
