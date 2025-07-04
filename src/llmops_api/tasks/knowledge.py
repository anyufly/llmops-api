from llmops_api.base.celery.base import app


@app.task(bind=True)
def split_document(self, content: bytes):
    pass


@app.task
def save_documents(
    self,
):
    pass
