from celery import Celery

from llmops_api.base.celery.serializer import register_msgpack_with_pydantic
from llmops_api.base.container.container import init_celery_container

container = init_celery_container()

register_msgpack_with_pydantic()


app = Celery()

app.conf.update(
    broker_url=container.config().celery.broker.url,
    result_backend=container.config().celery.result_backend.url,
    # 任务结果配置
    result_extended=True,  # 在SQLAlchemy中存储完整任务结果
    result_expires=container.config().celery.result_expires,  # 任务结果过期时间(秒)
    # 序列化配置
    accept_content=["msgpack-pydantic"],
    task_serializer="msgpack-pydantic",
    result_accept_content=["msgpack-pydantic"],
    result_serializer="msgpack-pydantic",
    # 任务管理配置
    worker_prefetch_multiplier=container.config().celery.worker_prefetch_multiplier,  # 预取任务数量
    task_acks_late=True,  # 任务完成后确认
    worker_max_tasks_per_child=container.config().celery.worker_max_tasks_per_child,  # 每个worker执行100次后重启
    # 时区配置
    timezone="Asia/Shanghai",
    enable_utc=True,
    database_table_schemas={
        "task": container.config().celery.result_backend.db_schema,
        "group": container.config().celery.result_backend.db_schema,
    },
    database_table_names={
        "task": "t_llmops_taskmeta",
        "group": "t_llmops_groupmeta",
    },
    # 数据库连接池配置 (SQLAlchemy backend)
    database_engine_options={
        "pool_size": container.config().celery.result_backend.pool.pool_size,
        "pool_recycle": container.config().celery.result_backend.pool.pool_recyle,
        "pool_timeout": container.config().celery.result_backend.pool.pool_timeout,
        "echo": container.config().celery.result_backend.echo,
    },
)

app.conf.task_routes = {}
