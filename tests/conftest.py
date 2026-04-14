"""Configure test environment before any imports that need env vars."""
import os

# Set required env vars for all tests
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
os.environ.setdefault("GITHUB_TOKEN", "ghp_test_token")
os.environ.setdefault("GITHUB_REPO", "owner/test-repo")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST-TOKEN")
os.environ.setdefault("TELEGRAM_CHAT_ID", "123456789")
