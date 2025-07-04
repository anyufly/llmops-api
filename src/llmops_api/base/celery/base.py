from celery import Celery

from llmops_api.base.container.container import init_container

app = Celery()
app.config_from_object("llmops_api.base.celery.config")

container = init_container()

app.container = container
