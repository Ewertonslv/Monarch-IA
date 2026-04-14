import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from tools.github_tools import GitHubTools


@pytest.fixture
def gh():
    with patch("tools.github_tools.Github") as MockGithub:
        mock_repo = MagicMock()
        MockGithub.return_value.get_repo.return_value = mock_repo
        tools = GitHubTools()
        tools._repo = mock_repo
        yield tools, mock_repo


def test_read_file(gh):
    tools, mock_repo = gh
    mock_file = MagicMock()
    mock_file.decoded_content = b"print('hello')"
    mock_repo.get_contents.return_value = mock_file

    result = tools.read_file("src/main.py")

    mock_repo.get_contents.assert_called_once_with("src/main.py")
    assert result == "print('hello')"


def test_list_files(gh):
    tools, mock_repo = gh
    f1 = MagicMock()
    f1.type = "file"
    f1.path = "src/a.py"
    f2 = MagicMock()
    f2.type = "dir"
    f2.path = "src/sub"
    f3 = MagicMock()
    f3.type = "file"
    f3.path = "src/sub/b.py"

    mock_repo.get_contents.side_effect = [
        [f1, f2],
        [f3],
    ]

    result = tools.list_files("src")
    assert "src/a.py" in result
    assert "src/sub/b.py" in result
    assert "src/sub" not in result


def test_write_file_creates_new(gh):
    tools, mock_repo = gh
    from github import GithubException
    mock_repo.get_contents.side_effect = GithubException(404, "not found", None)

    tools.write_file("new.py", "content", "feat: add new.py", "feature-branch")

    mock_repo.create_file.assert_called_once_with(
        "new.py", "feat: add new.py", "content", branch="feature-branch"
    )


def test_write_file_updates_existing(gh):
    tools, mock_repo = gh
    mock_existing = MagicMock()
    mock_existing.sha = "abc123"
    mock_repo.get_contents.return_value = mock_existing

    tools.write_file("existing.py", "new content", "fix: update", "main")

    mock_repo.update_file.assert_called_once_with(
        "existing.py", "fix: update", "new content", "abc123", branch="main"
    )


def test_create_branch(gh):
    tools, mock_repo = gh
    mock_ref = MagicMock()
    mock_ref.object.sha = "deadbeef"
    mock_repo.get_git_ref.return_value = mock_ref

    tools.create_branch("feature/new", from_branch="main")

    mock_repo.get_git_ref.assert_called_once_with("heads/main")
    mock_repo.create_git_ref.assert_called_once_with(
        ref="refs/heads/feature/new", sha="deadbeef"
    )


def test_create_pr(gh):
    tools, mock_repo = gh
    mock_pr = MagicMock()
    mock_pr.html_url = "https://github.com/owner/repo/pull/42"
    mock_repo.create_pull.return_value = mock_pr

    url = tools.create_pr(
        title="feat: new feature",
        body="Description",
        head="feature/new",
        base="main",
    )

    assert url == "https://github.com/owner/repo/pull/42"
    mock_repo.create_pull.assert_called_once_with(
        title="feat: new feature",
        body="Description",
        head="feature/new",
        base="main",
    )


def test_get_pr_diff(gh):
    tools, mock_repo = gh
    mock_pr = MagicMock()
    mock_file = MagicMock()
    mock_file.filename = "src/app.py"
    mock_file.patch = "@@ -1 +1 @@ print('x')"
    mock_pr.get_files.return_value = [mock_file]
    mock_repo.get_pull.return_value = mock_pr

    diff = tools.get_pr_diff(42)

    assert "src/app.py" in diff
    assert "@@ -1 +1 @@" in diff


def test_as_tools_schema_returns_list(gh):
    tools, _ = gh
    schema = tools.as_tools_schema()
    assert isinstance(schema, list)
    names = [t["name"] for t in schema]
    assert "read_file" in names
    assert "write_file" in names
    assert "create_branch" in names
    assert "create_pr" in names
    assert "list_files" in names
    assert "get_pr_diff" in names
