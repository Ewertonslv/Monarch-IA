import logging
from typing import Any

from github import Github, GithubException

from config import config

logger = logging.getLogger(__name__)


class GitHubTools:
    """Wraps PyGithub for common operations used by Monarch AI agents."""

    def __init__(self) -> None:
        self._github = Github(config.github_token)
        self._repo = self._github.get_repo(config.github_repo)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def read_file(self, path: str, ref: str | None = None) -> str:
        """Return decoded file content from the repository."""
        kwargs: dict[str, Any] = {}
        if ref:
            kwargs["ref"] = ref
        contents = self._repo.get_contents(path, **kwargs)
        return contents.decoded_content.decode("utf-8")

    def list_files(self, directory: str = "", ref: str | None = None) -> list[str]:
        """Recursively list all file paths under *directory*."""
        kwargs: dict[str, Any] = {}
        if ref:
            kwargs["ref"] = ref

        paths: list[str] = []
        queue = [directory]

        while queue:
            current = queue.pop()
            items = self._repo.get_contents(current, **kwargs)
            if not isinstance(items, list):
                items = [items]
            for item in items:
                if item.type == "dir":
                    queue.append(item.path)
                else:
                    paths.append(item.path)

        return sorted(paths)

    def get_pr_diff(self, pr_number: int) -> str:
        """Return a unified-diff-style string for all files in the PR."""
        pr = self._repo.get_pull(pr_number)
        lines: list[str] = []
        for f in pr.get_files():
            lines.append(f"--- {f.filename}")
            if f.patch:
                lines.append(f.patch)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def write_file(
        self,
        path: str,
        content: str,
        commit_message: str,
        branch: str,
    ) -> None:
        """Create or update *path* on *branch* with *content*."""
        try:
            existing = self._repo.get_contents(path, ref=branch)
            self._repo.update_file(
                path, commit_message, content, existing.sha, branch=branch
            )
            logger.info("Updated %s on %s", path, branch)
        except GithubException as exc:
            if exc.status == 404:
                self._repo.create_file(path, commit_message, content, branch=branch)
                logger.info("Created %s on %s", path, branch)
            else:
                raise

    def create_branch(self, branch_name: str, from_branch: str = "main") -> None:
        """Create a new branch from *from_branch*."""
        ref = self._repo.get_git_ref(f"heads/{from_branch}")
        sha = ref.object.sha
        self._repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=sha)
        logger.info("Created branch %s from %s", branch_name, from_branch)

    def create_pr(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> str:
        """Open a pull request and return its HTML URL."""
        pr = self._repo.create_pull(title=title, body=body, head=head, base=base)
        logger.info("Created PR #%s: %s", pr.number, pr.html_url)
        return pr.html_url

    # ------------------------------------------------------------------
    # Tool schema for Anthropic tool_use
    # ------------------------------------------------------------------

    def as_tools_schema(self) -> list[dict[str, Any]]:
        """Return the Anthropic tool_use schema for all GitHub tools."""
        return [
            {
                "name": "read_file",
                "description": "Read the content of a file from the GitHub repository.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path in the repo"},
                        "ref": {
                            "type": "string",
                            "description": "Branch, tag, or commit SHA (default: default branch)",
                        },
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "list_files",
                "description": "List all files recursively under a directory in the repository.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path (empty string for root)",
                        },
                        "ref": {"type": "string", "description": "Branch or commit SHA"},
                    },
                    "required": [],
                },
            },
            {
                "name": "write_file",
                "description": "Create or update a file in the repository on a specific branch.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string", "description": "Full file content"},
                        "commit_message": {"type": "string"},
                        "branch": {"type": "string"},
                    },
                    "required": ["path", "content", "commit_message", "branch"],
                },
            },
            {
                "name": "create_branch",
                "description": "Create a new git branch in the repository.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "branch_name": {"type": "string"},
                        "from_branch": {
                            "type": "string",
                            "description": "Source branch (default: main)",
                        },
                    },
                    "required": ["branch_name"],
                },
            },
            {
                "name": "create_pr",
                "description": "Open a pull request and return its URL.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "body": {"type": "string", "description": "PR description in Markdown"},
                        "head": {"type": "string", "description": "Source branch"},
                        "base": {"type": "string", "description": "Target branch (default: main)"},
                    },
                    "required": ["title", "body", "head"],
                },
            },
            {
                "name": "get_pr_diff",
                "description": "Get the unified diff of all files changed in a pull request.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pr_number": {"type": "integer", "description": "Pull request number"},
                    },
                    "required": ["pr_number"],
                },
            },
        ]
