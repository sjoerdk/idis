from celery import shared_task


@shared_task
def run_test_task():
    print("SHARED TASK WAS RUN")
