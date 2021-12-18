from celery import Celery
from time import sleep
from celery.utils.log import get_task_logger

celery = Celery(__name__)
##############redis
# celery.conf.broker_url = "redis://localhost:6379/3"
# celery.conf.result_backend = "db+postgresql://postgres:1@localhost:5432/api"
##############rabbitmq
celery.conf.broker_url = "amqp://guest:guest@127.0.0.1:5672//"
celery.conf.result_backend = "db+postgresql://postgres:1@localhost:5432/api"
celery_log = get_task_logger(__name__)



@celery.task(name="create_task")
def create_task(name, quantity):
    complete_time_per_item = 5
    sleep(complete_time_per_item * quantity)
    celery_log.info(f"Order Complete!")
    return {"message": f"Hi {name}, Your order has completed!",
            "order_quantity": quantity}
