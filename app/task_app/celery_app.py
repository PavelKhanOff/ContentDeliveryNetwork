from celery import Celery
from eduone_cdn.app.settings.config import CELERY_BACKEND_URL, CELERY_BROKER_URL


app = Celery(
    "worker",
    backend=CELERY_BACKEND_URL,
    broker=CELERY_BROKER_URL,
)
app.conf.result_backend_transport_options = {'master_name': "mymaster"}
app.autodiscover_tasks(['eduone_cdn.app.core'])
