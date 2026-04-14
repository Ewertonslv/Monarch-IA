import os
from unittest.mock import patch


def test_config_loads_required_vars():
    env = {
        "ANTHROPIC_API_KEY": "sk-test",
        "GITHUB_TOKEN": "ghp_test",
        "GITHUB_REPO": "owner/repo",
        "TELEGRAM_BOT_TOKEN": "123:abc",
        "TELEGRAM_CHAT_ID": "456",
    }
    with patch.dict(os.environ, env):
        import importlib
        import config as cfg_module
        importlib.reload(cfg_module)
        c = cfg_module.Config()
        assert c.anthropic_api_key == "sk-test"
        assert c.github_repo == "owner/repo"
        assert c.max_agent_retries == 3
        assert c.confidence_threshold == 0.70


def test_config_raises_on_empty_key():
    env = {
        "ANTHROPIC_API_KEY": "",
        "GITHUB_TOKEN": "ghp_test",
        "GITHUB_REPO": "owner/repo",
        "TELEGRAM_BOT_TOKEN": "123:abc",
        "TELEGRAM_CHAT_ID": "456",
    }
    import pytest
    with patch.dict(os.environ, env):
        import config as cfg_module
        with pytest.raises(Exception):
            cfg_module.Config()
