import uuid
from celery import shared_task

from idis.jobs.models import Job


@shared_task
def process_job(*, job_pk: uuid.UUID):
    _ = Job.objects.get(pk=job_pk)

    # check world
    # get data
    # modify
    # send to CTP
    # wait for all files to come out on the other end
    # copy data
