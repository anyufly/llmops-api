# config = load_config()
from llmops_api.base.config.config import Config, CorsConfig, DatabaseConfig, load_config

__all__ = ["load_config", "Config", "DatabaseConfig", "CorsConfig"]
