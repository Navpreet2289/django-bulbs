from celery import shared_task
import requests

from django.conf import settings
from django.utils import timezone


@shared_task(default_retry_delay=5)
def firebase_update_timestamp(liveblog_id):
    endpoint = getattr(settings, 'LIVEBLOG_FIREBASE_NOTIFY_ENDPOINT', None)
    if endpoint:
        url = endpoint.format(liveblog_id=liveblog_id)
        requests.put(url, json={
            'updatedAt': timezone.now().timestamp()  # TODO: What time format?
        })
