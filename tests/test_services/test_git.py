"""Tests for Git service."""

import pytest

from xenv_cli.services.git import GitService, GitError


class TestSlugifyOrigin:
    """Tests for origin URL slugification."""

    def test_ssh_origin(self):
        """SSH URLs are correctly slugified."""
        assert (
            GitService.slugify_origin("git@github.com:user/repo.git")
            == "github.com-user-repo"
        )

    def test_https_origin(self):
        """HTTPS URLs are correctly slugified."""
        assert (
            GitService.slugify_origin("https://github.com/user/repo.git")
            == "github.com-user-repo"
        )

    def test_http_origin(self):
        """HTTP URLs are correctly slugified."""
        assert (
            GitService.slugify_origin("http://github.com/user/repo.git")
            == "github.com-user-repo"
        )

    def test_no_git_suffix(self):
        """URLs without .git suffix work."""
        assert (
            GitService.slugify_origin("git@github.com:user/repo")
            == "github.com-user-repo"
        )

    def test_gitlab_origin(self):
        """GitLab URLs work."""
        assert (
            GitService.slugify_origin("git@gitlab.com:org/project.git")
            == "gitlab.com-org-project"
        )

    def test_nested_path(self):
        """Nested paths are handled."""
        assert (
            GitService.slugify_origin("git@github.com:org/team/repo.git")
            == "github.com-org-team-repo"
        )


class TestGitService:
    """Tests for GitService methods."""

    def test_get_root_in_repo(self, git_repo):
        """get_root returns repo root when in a git repo."""
        service = GitService()
        root = service.get_root(git_repo)
        # Resolve symlinks for comparison (macOS /var -> /private/var)
        assert root.resolve() == git_repo.resolve()

    def test_get_root_not_in_repo(self, temp_dir):
        """get_root raises GitError when not in a git repo."""
        service = GitService()
        with pytest.raises(GitError, match="Not a git repository"):
            service.get_root(temp_dir)

    def test_get_origin(self, git_repo):
        """get_origin returns the remote origin."""
        service = GitService()
        origin = service.get_origin(git_repo)
        assert origin == "git@github.com:test/repo.git"

    def test_is_git_repo_true(self, git_repo):
        """is_git_repo returns True in a git repo."""
        service = GitService()
        assert service.is_git_repo(git_repo) is True

    def test_is_git_repo_false(self, temp_dir):
        """is_git_repo returns False outside a git repo."""
        service = GitService()
        assert service.is_git_repo(temp_dir) is False
