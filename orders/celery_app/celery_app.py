from os import environ, getenv

from celery import Celery
from dotenv import load_dotenv

# from celery.exceptions import Ignore
# from celery.result import AsyncResult

# from send_mail import send_mail

environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

load_dotenv()
CELERY_REDIS_DB_HOST = getenv("CELERY_REDIS_DB_HOST")
CELERY_REDIS_DB_PORT = getenv("CELERY_REDIS_DB_PORT")
CELERY_REDIS_BACKEND = getenv("CELERY_REDIS_BACKEND")
CELERY_REDIS_BROKER = getenv("CELERY_REDIS_BROKER")

celery_app = Celery("orders", backend=f"redis://{CELERY_REDIS_DB_HOST}:{CELERY_REDIS_DB_PORT}/{CELERY_REDIS_BACKEND}",
                    broker=f"redis://{CELERY_REDIS_DB_HOST}:{CELERY_REDIS_DB_PORT}/{CELERY_REDIS_BROKER}",
                    broker_connection_retry_on_startup=True)

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

# def get_task(task_id: str) -> AsyncResult:
#     return AsyncResult(task_id, app=celery_app)

# @celery_app.task(name='send_mail_message', bind=True)
# def send_mail_message(self, subject, body, from_email, to_email):
#     try:
#         return send_mail(subject, body, from_email, to_email)
#     except Exception as ex:
#         self.update_state(state=states.FAILURE,
#                           meta={'exc_type': type(ex).__name__, 'exc_message': traceback.format_exc().split('\n'), })
#         raise Ignore()
