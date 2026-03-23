"""Configuration loading utilities."""

import os
from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str = "config/settings.yaml") -> dict[str, Any]:
    """Load configuration from YAML file with environment variable overrides."""
    
    path = Path(config_path)
    if not path.exists():
        # Try relative to project root
        path = Path(__file__).parent.parent.parent / config_path
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Environment variable overrides
    config = _apply_env_overrides(config)
    
    return config


def _apply_env_overrides(config: dict) -> dict:
    """Apply environment variable overrides to config."""
    
    # LLM settings
    if os.getenv("LLM_PROVIDER"):
        config.setdefault("llm", {})["provider"] = os.getenv("LLM_PROVIDER")
    
    if os.getenv("LLM_MODEL"):
        config.setdefault("llm", {})["model"] = os.getenv("LLM_MODEL")
    
    # Feature request override
    if os.getenv("FEATURE_REQUEST"):
        config["feature_request"] = os.getenv("FEATURE_REQUEST")
    
    # Deliberation settings
    if os.getenv("MIN_ROUNDS"):
        config.setdefault("deliberation", {})["min_rounds"] = int(os.getenv("MIN_ROUNDS"))
    
    if os.getenv("MAX_ROUNDS"):
        config.setdefault("deliberation", {})["max_rounds"] = int(os.getenv("MAX_ROUNDS"))
    
    return config