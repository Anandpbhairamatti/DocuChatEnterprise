from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.worker.tasks']
)

celery_app.conf.broker_transport_options = {"protocol": 2}
celery_app.conf.result_backend_transport_options = {"protocol": 2}

