from io import StringIO

import pytest
import yaml
from pydantic_core import ValidationError

from ovo.core.configuration import OVOConfig, ConfigProps, DEFAULT_OVO_HOME


def test_config_default():
    data = yaml.safe_load(StringIO(OVOConfig.default(ConfigProps())))
    data["dir"] = DEFAULT_OVO_HOME
    config = OVOConfig(**data)


def test_config_with_extra_args():
    with pytest.raises(ValidationError):
        data = yaml.safe_load(StringIO(OVOConfig.default(ConfigProps())))
        data["dir"] = DEFAULT_OVO_HOME
        data["foo"] = "bar"
        config = OVOConfig(**data)


def test_env_var_overrides_top_level_field(monkeypatch):
    """OVO_* env vars must take precedence over values loaded from config.yml."""
    monkeypatch.setenv("OVO_LOCAL_SCHEDULER", "scheduler_from_env")
    data = yaml.safe_load(StringIO(OVOConfig.default(ConfigProps())))
    data["dir"] = DEFAULT_OVO_HOME
    # sanity check: the YAML sets a different value
    assert data["local_scheduler"] != "scheduler_from_env"
    config = OVOConfig(**data)
    assert config.local_scheduler == "scheduler_from_env"


def test_env_var_overrides_nested_field(monkeypatch):
    """Nested overrides via the __ delimiter, e.g. OVO_STORAGE__VERBOSE and OVO_DB__URL."""
    monkeypatch.setenv("OVO_STORAGE__VERBOSE", "true")
    monkeypatch.setenv("OVO_DB__URL", "sqlite:///env_override.db")
    data = yaml.safe_load(StringIO(OVOConfig.default(ConfigProps())))
    data["dir"] = DEFAULT_OVO_HOME
    assert data["storage"]["verbose"] is False
    config = OVOConfig(**data)
    assert config.storage.verbose is True
    assert config.db.url.endswith("env_override.db")


def test_config_without_env_uses_yaml(monkeypatch):
    """Without env vars, values come from the config.yml as before."""
    for key in ("OVO_LOCAL_SCHEDULER", "OVO_STORAGE__VERBOSE", "OVO_DB__URL"):
        monkeypatch.delenv(key, raising=False)
    data = yaml.safe_load(StringIO(OVOConfig.default(ConfigProps())))
    data["dir"] = DEFAULT_OVO_HOME
    config = OVOConfig(**data)
    assert config.local_scheduler == data["local_scheduler"]
