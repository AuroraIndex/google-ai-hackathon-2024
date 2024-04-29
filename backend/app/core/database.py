from google.cloud import storage, firestore_v1

from app.core.logger import logger

try:
    db = firestore_v1.AsyncClient(database="sandbox")
    logger.info("db connected")
except Exception as e:
    db = None
    logger.exception(e)

try:
    storage = storage.Client()
    logger.info('blob connected')
except Exception as e:
    storage = None
    logger.exception(e)
