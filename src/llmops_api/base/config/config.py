import os
from dataclasses import dataclass
from typing import Annotated, Any, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field, computed_field, model_validator

from llmops_api.const.constant import (
    DEBUG_MODE,
    DEFAULT_ACCESS_TOKEN_EXPIRE,
    DEFAULT_CELERY_BACKEND_DATABASE_DB,
    DEFAULT_CELERY_BACKEND_DATABASE_HOST,
    DEFAULT_CELERY_BACKEND_DATABASE_PORT,
    DEFAULT_CELERY_BACKEND_DATABASE_SCHEMA,
    DEFAULT_CELERY_BACKEND_DATABASE_USER,
    DEFAULT_CELERY_BACKEND_SQLALCHEMY_ECHO,
    DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_MAX_OVERFLOW,
    DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_RECYLE,
    DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_SIZE,
    DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_TIMEOUT,
    DEFAULT_CORS_ALLOW_CREDENTIALS,
    DEFAULT_CORS_ALLOW_HEADERS,
    DEFAULT_CORS_ALLOW_METHODS,
    DEFAULT_CORS_ALLOW_ORIGINS,
    DEFAULT_CORS_EXPOSE_HEADERS,
    DEFAULT_CORS_MAX_AGE,
    DEFAULT_DATABASE_DB,
    DEFAULT_DATABASE_HOST,
    DEFAULT_DATABASE_PORT,
    DEFAULT_DATABASE_SCHEMA,
    DEFAULT_DATABASE_USER,
    DEFAULT_LOGGER_LEVEL,
    DEFAULT_RABBITMQ_HOST,
    DEFAULT_RABBITMQ_PORT,
    DEFAULT_RABBITMQ_USERNAME,
    DEFAULT_RABBITMQ_VHOST,
    DEFAULT_REDIS_DB,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
    DEFAULT_REDIS_USER_NAME,
    DEFAULT_REFRESH_TOKEN_EXPIRE,
    DEFAULT_RESULT_EXPIRES,
    DEFAULT_SQLALCHEMY_ECHO,
    DEFAULT_SQLALCHEMY_POOL_MAX_OVERFLOW,
    DEFAULT_SQLALCHEMY_POOL_RECYLE,
    DEFAULT_SQLALCHEMY_POOL_SIZE,
    DEFAULT_SQLALCHEMY_POOL_TIMEOUT,
    DEFAULT_WORKER_MAX_TASKS_PER_CHILD,
    DEFAULT_WORKER_PREFETCH_MULTIPLIER,
)


@dataclass
class EnvField:
    env: str


class FromEnvBase(BaseModel):
    @classmethod
    def from_env(cls):
        value_dict = {}
        for field_name, field_info in cls.model_fields.items():
            if issubclass(field_info.annotation, FromEnvBase):  # pyright: ignore[reportArgumentType]
                value_dict[field_name] = field_info.annotation.from_env()
            for meta in field_info.metadata:
                if isinstance(meta, EnvField):
                    value_dict[field_name] = os.getenv(meta.env)
        return cls.model_validate(value_dict)


class ConfigBase(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def set_none_default(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # 获取模型字段定义
        model_fields = cls.model_fields

        # 遍历所有字段
        for field_name, field_info in model_fields.items():
            # 如果字段值为 None 且有默认值
            if data.get(field_name) is None:
                # 优先使用 default_factory
                if field_info.default_factory is not None:
                    data[field_name] = field_info.default_factory()  # type: ignore
                # 使用静态默认值
                elif field_info.default is not None:
                    data[field_name] = field_info.default
        return data


class EnvirementConfig(ConfigBase, FromEnvBase):
    debug_mode: Annotated[bool, Field(default=DEBUG_MODE), EnvField(env="DEBUG_MODE")]


class LoggerConfig(ConfigBase, FromEnvBase):
    level: Annotated[str, Field(default=DEFAULT_LOGGER_LEVEL), EnvField(env="COMMON_LOG_LEVEL")]


class SqlAlchemyPoolConfig(ConfigBase, FromEnvBase):
    pool_size: Annotated[
        int, Field(default=DEFAULT_SQLALCHEMY_POOL_SIZE), EnvField(env="SQLALCHEMY_POOL_SIZE")
    ]

    max_overflow: Annotated[
        int,
        Field(default=DEFAULT_SQLALCHEMY_POOL_MAX_OVERFLOW),
        EnvField(env="SQLALCHEMY_POOL_MAX_OVERFLOW"),
    ]

    pool_recyle: Annotated[
        int,
        Field(default=DEFAULT_SQLALCHEMY_POOL_RECYLE),
        EnvField(env="SQLALCHEMY_POOL_RECYLE"),
    ]
    pool_timeout: Annotated[
        int,
        Field(default=DEFAULT_SQLALCHEMY_POOL_TIMEOUT),
        EnvField(env="SQLALCHEMY_POOL_TIMEOUT"),
    ]


class DatabaseConfig(ConfigBase, FromEnvBase):
    host: Annotated[str, Field(default=DEFAULT_DATABASE_HOST), EnvField(env="DATABASE_HOST")]
    port: Annotated[str, Field(default=DEFAULT_DATABASE_PORT), EnvField(env="DATABASE_PORT")]
    db: Annotated[str, Field(default=DEFAULT_DATABASE_DB), EnvField(env="DATABASE_DB")]
    user: Annotated[str, Field(default=DEFAULT_DATABASE_USER), EnvField(env="DATABASE_USER")]
    db_schema: Annotated[
        str, Field(default=DEFAULT_DATABASE_SCHEMA), EnvField(env="DATABASE_SCHEMA")
    ]
    password: Annotated[str, EnvField(env="DATABASE_PASSWORD")]
    pool: SqlAlchemyPoolConfig
    echo: Annotated[
        bool,
        Field(default=DEFAULT_SQLALCHEMY_ECHO),
        EnvField(env="SQLALCHEMY_ECHO"),
    ]

    @computed_field
    def url(self) -> str:
        # DATABASE_URL=postgresql+asyncpg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_DB}
        url = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        return url

    @computed_field
    def sync_url(self) -> str:
        url = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        return url


class CorsConfig(ConfigBase, FromEnvBase):
    allow_origins_str: Annotated[
        str, Field(default=DEFAULT_CORS_ALLOW_ORIGINS), EnvField(env="CORS_ALLOW_ORIGINS")
    ]
    allow_credentials: Annotated[
        bool, Field(default=DEFAULT_CORS_ALLOW_CREDENTIALS), EnvField(env="CORS_ALLOW_CREDENTIALS")
    ]
    allow_methods_str: Annotated[
        str, Field(default=DEFAULT_CORS_ALLOW_METHODS), EnvField(env="CORS_ALLOW_METHODS")
    ]
    allow_headers_str: Annotated[
        str, Field(default=DEFAULT_CORS_ALLOW_HEADERS), EnvField(env="CORS_ALLOW_HEADERS")
    ]
    expose_headers_str: Annotated[
        str, Field(default=DEFAULT_CORS_EXPOSE_HEADERS), EnvField(env="CORS_EXPOSE_HEADERS")
    ]
    max_age: Annotated[int, Field(default=DEFAULT_CORS_MAX_AGE), EnvField(env="CORS_MAX_AGE")]

    @computed_field
    def allow_origins(self) -> List[str]:
        if self.allow_origins_str == "":
            return []
        return self.allow_origins_str.split(",")

    @computed_field
    def allow_methods(self) -> List[str]:
        if self.allow_methods_str == "":
            return []
        return self.allow_methods_str.split(",")

    @computed_field
    def allow_headers(self) -> List[str]:
        if self.allow_headers_str == "":
            return []
        return self.allow_headers_str.split(",")

    @computed_field
    def expose_headers(self) -> List[str]:
        if self.expose_headers_str == "":
            return []
        return self.expose_headers_str.split(",")


class RedisConfig(ConfigBase, FromEnvBase):
    username: Annotated[
        str, Field(default=DEFAULT_REDIS_USER_NAME), EnvField(env="REDIS_USER_NAME")
    ]
    password: Annotated[str, EnvField(env="REDIS_PASSWORD")]
    host: Annotated[str, Field(default=DEFAULT_REDIS_HOST), EnvField(env="REDIS_HOST")]

    port: Annotated[str, Field(default=DEFAULT_REDIS_PORT), EnvField(env="REDIS_PORT)")]

    db: Annotated[int, Field(default=DEFAULT_REDIS_DB), EnvField(env="REDIS_DB")]

    @computed_field
    def url(self) -> str:
        url = f"redis://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}"
        return url


class AuthConfig(ConfigBase, FromEnvBase):
    access_token_expire: Annotated[
        int,
        Field(default=DEFAULT_ACCESS_TOKEN_EXPIRE),
        EnvField(env="ACCESS_TOKEN_EXPIRE"),
    ]

    refresh_token_expire: Annotated[
        int,
        Field(default=DEFAULT_REFRESH_TOKEN_EXPIRE),
        EnvField(env="REFRESH_TOKEN_EXPIRE"),
    ]


class BrokerConfig(ConfigBase, FromEnvBase):
    username: Annotated[
        str, Field(default=DEFAULT_RABBITMQ_USERNAME), EnvField(env="RABBITMQ_USERNAME")
    ]
    password: Annotated[str, EnvField(env="RABBITMQ_PASSWORD")]
    host: Annotated[str, Field(default=DEFAULT_RABBITMQ_HOST), EnvField(env="RABBITMQ_HOST")]
    port: Annotated[str, Field(default=DEFAULT_RABBITMQ_PORT), EnvField(env="RABBITMQ_PORT")]
    vhost: Annotated[str, Field(default=DEFAULT_RABBITMQ_VHOST), EnvField(env="RABBITMQ_VHOST")]

    @computed_field
    def url(self) -> str:
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.vhost}"


class ResultBackendPoolConfig(ConfigBase, FromEnvBase):
    pool_size: Annotated[
        int,
        Field(default=DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_SIZE),
        EnvField(env="CELERY_BACKEND_SQLALCHEMY_POOL_SIZE"),
    ]

    max_overflow: Annotated[
        int,
        Field(default=DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_MAX_OVERFLOW),
        EnvField(env="CELERY_BACKEND_SQLALCHEMY_POOL_MAX_OVERFLOW"),
    ]

    pool_recyle: Annotated[
        int,
        Field(default=DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_RECYLE),
        EnvField(env="CELERY_BACKEND_SQLALCHEMY_POOL_RECYLE"),
    ]
    pool_timeout: Annotated[
        int,
        Field(default=DEFAULT_CELERY_BACKEND_SQLALCHEMY_POOL_TIMEOUT),
        EnvField(env="CELERY_BACKEND_SQLALCHEMY_POOL_TIMEOUT"),
    ]


class ResultBackendConfig(ConfigBase, FromEnvBase):
    host: Annotated[
        str,
        Field(default=DEFAULT_CELERY_BACKEND_DATABASE_HOST),
        EnvField(env="CELERY_BACKEND_DATABASE_HOST"),
    ]
    port: Annotated[
        str,
        Field(default=DEFAULT_CELERY_BACKEND_DATABASE_PORT),
        EnvField(env="CELERY_BACKEND_DATABASE_PORT"),
    ]
    db: Annotated[
        str,
        Field(default=DEFAULT_CELERY_BACKEND_DATABASE_DB),
        EnvField(env="CELERY_BACKEND_DATABASE_DB"),
    ]
    user: Annotated[
        str,
        Field(default=DEFAULT_CELERY_BACKEND_DATABASE_USER),
        EnvField(env="CELERY_BACKEND_DATABASE_USER"),
    ]
    password: Annotated[str, EnvField(env="CELERY_BACKEND_DATABASE_PASSWORD")]
    db_schema: Annotated[
        str,
        Field(default=DEFAULT_CELERY_BACKEND_DATABASE_SCHEMA),
        EnvField(env="CELERY_BACKEND_DATABASE_SCHEMA"),
    ]

    pool: ResultBackendPoolConfig

    echo: Annotated[
        bool,
        Field(default=DEFAULT_CELERY_BACKEND_SQLALCHEMY_ECHO),
        EnvField(env="CELERY_BACKEND_SQLALCHEMY_ECHO"),
    ]

    @computed_field
    def url(self) -> str:
        return f"db+postgresql+psycopg://{self.user}:{self.password}@{self.host}/{self.db}"


class CeleryConfig(ConfigBase, FromEnvBase):
    broker: BrokerConfig
    result_backend: ResultBackendConfig
    worker_prefetch_multiplier: Annotated[
        int,
        Field(default=DEFAULT_WORKER_PREFETCH_MULTIPLIER),
        EnvField(env="WORKER_PREFETCH_MULTIPLIER"),
    ]  # 预取任务数量
    worker_max_tasks_per_child: Annotated[
        int,
        Field(default=DEFAULT_WORKER_MAX_TASKS_PER_CHILD),
        EnvField(env="WORKER_MAX_TASKS_PER_CHILD"),
    ]
    result_expires: Annotated[
        int, Field(default=DEFAULT_RESULT_EXPIRES), EnvField(env="RESULT_EXPIRES")
    ]


class Config(FromEnvBase):
    """
    项目配置
    """

    env: EnvirementConfig
    database: DatabaseConfig

    logger: LoggerConfig
    cors: CorsConfig
    redis: RedisConfig
    auth: AuthConfig
    celery: CeleryConfig


def load_config():
    load_dotenv()
    config = Config.from_env()
    return config
