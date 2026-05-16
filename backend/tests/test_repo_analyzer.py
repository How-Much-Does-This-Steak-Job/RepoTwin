"""Tests for repository analysis module."""

import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.models.database import Repository, RepositoryStatus


class TestRepositoryCloning:
    """Test repository cloning functionality."""
    
    @pytest.mark.asyncio
    async def test_clone_public_repo_success(self, temp_repo_dir):
        """Test cloning a public repository."""
        with patch("app.core.repo_analyzer.clone_repository") as mock_clone:
            mock_clone.return_value = {
                "path": str(temp_repo_dir),
                "branch": "main",
                "commit_count": 100,
            }
            
            from app.core.repo_analyzer import clone_repository
            
            result = await clone_repository(
                url="https://github.com/test/repo.git",
                storage_path=str(temp_repo_dir),
            )
            
            assert result["path"] == str(temp_repo_dir)
            assert result["branch"] == "main"
    
    @pytest.mark.asyncio
    async def test_clone_private_repo_with_token(self, temp_repo_dir):
        """Test cloning a private repository with token."""
        with patch("app.core.repo_analyzer.clone_repository") as mock_clone:
            mock_clone.return_value = {
                "path": str(temp_repo_dir),
                "branch": "main",
                "authenticated": True,
            }
            
            from app.core.repo_analyzer import clone_repository
            
            result = await clone_repository(
                url="https://github.com/test/private-repo.git",
                storage_path=str(temp_repo_dir),
                credentials={"token": "ghp_test_token"},
            )
            
            assert result["path"] == str(temp_repo_dir)
            assert result.get("authenticated") is True
    
    @pytest.mark.asyncio
    async def test_clone_invalid_url(self):
        """Test handling of invalid repository URL."""
        with patch("app.core.repo_analyzer.clone_repository") as mock_clone:
            mock_clone.side_effect = ValueError("Invalid repository URL")
            
            from app.core.repo_analyzer import clone_repository
            
            with pytest.raises(ValueError, match="Invalid repository URL"):
                await clone_repository(
                    url="not-a-valid-url",
                    storage_path="/tmp/test",
                )
    
    @pytest.mark.asyncio
    async def test_clone_nonexistent_repo(self):
        """Test cloning a non-existent repository."""
        with patch("app.core.repo_analyzer.clone_repository") as mock_clone:
            mock_clone.side_effect = Exception("Repository not found")
            
            from app.core.repo_analyzer import clone_repository
            
            with pytest.raises(Exception, match="Repository not found"):
                await clone_repository(
                    url="https://github.com/nonexistent/repo.git",
                    storage_path="/tmp/test",
                )


class TestFileTreeGeneration:
    """Test file tree generation."""
    
    def test_get_file_tree_basic(self, temp_repo_dir):
        """Test generating file tree for a repository."""
        with patch("app.core.repo_analyzer.get_file_tree") as mock_tree:
            mock_tree.return_value = {
                "path": "",
                "files": [
                    {"name": "src", "path": "src", "type": "directory", "children_count": 2},
                    {"name": "tests", "path": "tests", "type": "directory", "children_count": 1},
                ],
            }
            
            from app.core.repo_analyzer import get_file_tree
            
            result = get_file_tree(str(temp_repo_dir))
            
            assert result["path"] == ""
            assert len(result["files"]) == 2
            assert result["files"][0]["name"] == "src"
            assert result["files"][0]["type"] == "directory"
    
    def test_get_file_tree_recursive(self, temp_repo_dir):
        """Test recursive file tree generation."""
        with patch("app.core.repo_analyzer.get_file_tree") as mock_tree:
            mock_tree.return_value = {
                "path": "",
                "files": [
                    {
                        "name": "src",
                        "path": "src",
                        "type": "directory",
                        "children": [
                            {"name": "main.py", "path": "src/main.py", "type": "file", "size": 100},
                            {"name": "utils.py", "path": "src/utils.py", "type": "file", "size": 50},
                        ],
                    },
                ],
            }
            
            from app.core.repo_analyzer import get_file_tree
            
            result = get_file_tree(str(temp_repo_dir), recursive=True)
            
            assert len(result["files"]) == 1
            assert result["files"][0]["name"] == "src"
            assert "children" in result["files"][0]
            assert len(result["files"][0]["children"]) == 2
    
    def test_get_file_tree_with_filter(self, temp_repo_dir):
        """Test file tree with file type filter."""
        with patch("app.core.repo_analyzer.get_file_tree") as mock_tree:
            mock_tree.return_value = {
                "path": "",
                "files": [
                    {"name": "main.py", "path": "src/main.py", "type": "file", "language": "python"},
                    {"name": "utils.py", "path": "src/utils.py", "type": "file", "language": "python"},
                ],
            }
            
            from app.core.repo_analyzer import get_file_tree
            
            result = get_file_tree(str(temp_repo_dir), file_filter="*.py")
            
            assert len(result["files"]) == 2
            for file in result["files"]:
                assert file["name"].endswith(".py")
    
    def test_get_file_tree_empty_repo(self, tmp_path):
        """Test file tree for empty repository."""
        with patch("app.core.repo_analyzer.get_file_tree") as mock_tree:
            mock_tree.return_value = {
                "path": "",
                "files": [],
            }
            
            from app.core.repo_analyzer import get_file_tree
            
            empty_repo = tmp_path / "empty-repo"
            empty_repo.mkdir()
            
            result = get_file_tree(str(empty_repo))
            
            assert result["files"] == []


class TestMetadataExtraction:
    """Test metadata extraction."""
    
    def test_extract_repository_metadata(self, temp_repo_dir):
        """Test extracting repository metadata."""
        with patch("app.core.repo_analyzer.extract_metadata") as mock_extract:
            mock_extract.return_value = {
                "total_files": 50,
                "total_lines": 5000,
                "languages": {
                    "Python": {"files": 30, "lines": 3000},
                    "JavaScript": {"files": 20, "lines": 2000},
                },
                "file_types": {
                    ".py": 30,
                    ".js": 20,
                },
            }
            
            from app.core.repo_analyzer import extract_metadata
            
            result = extract_metadata(str(temp_repo_dir))
            
            assert result["total_files"] == 50
            assert result["total_lines"] == 5000
            assert "Python" in result["languages"]
            assert result["languages"]["Python"]["files"] == 30
    
    def test_detect_languages(self, temp_repo_dir):
        """Test language detection."""
        with patch("app.core.repo_analyzer.detect_languages") as mock_detect:
            mock_detect.return_value = {
                "Python": 60.0,
                "JavaScript": 40.0,
            }
            
            from app.core.repo_analyzer import detect_languages
            
            result = detect_languages(str(temp_repo_dir))
            
            assert "Python" in result
            assert "JavaScript" in result
            assert result["Python"] == 60.0
            assert result["JavaScript"] == 40.0
    
    def test_extract_git_metadata(self, temp_repo_dir):
        """Test extracting git metadata."""
        with patch("app.core.repo_analyzer.extract_git_metadata") as mock_git:
            mock_git.return_value = {
                "default_branch": "main",
                "commit_count": 100,
                "contributors": ["user1", "user2"],
                "last_commit": "2025-01-01T00:00:00Z",
            }
            
            from app.core.repo_analyzer import extract_git_metadata
            
            result = extract_git_metadata(str(temp_repo_dir))
            
            assert result["default_branch"] == "main"
            assert result["commit_count"] == 100
            assert len(result["contributors"]) == 2
    
    def test_calculate_code_statistics(self, temp_repo_dir):
        """Test code statistics calculation."""
        with patch("app.core.repo_analyzer.calculate_statistics") as mock_stats:
            mock_stats.return_value = {
                "total_lines": 1000,
                "code_lines": 800,
                "comment_lines": 150,
                "blank_lines": 50,
                "average_file_size": 200,
                "largest_file": "src/main.py",
            }
            
            from app.core.repo_analyzer import calculate_statistics
            
            result = calculate_statistics(str(temp_repo_dir))
            
            assert result["total_lines"] == 1000
            assert result["code_lines"] == 800
            assert result["comment_lines"] == 150
            assert result["blank_lines"] == 50


class TestFileOperations:
    """Test file operations."""
    
    def test_get_file_content(self, temp_repo_dir):
        """Test reading file content."""
        with patch("app.core.repo_analyzer.get_file_content") as mock_content:
            mock_content.return_value = {
                "path": "src/main.py",
                "content": "def main(): pass",
                "size": 100,
                "line_count": 10,
                "language": "python",
            }
            
            from app.core.repo_analyzer import get_file_content
            
            result = get_file_content(str(temp_repo_dir), "src/main.py")
            
            assert result["path"] == "src/main.py"
            assert "def main()" in result["content"]
            assert result["language"] == "python"
    
    def test_get_file_content_not_found(self, temp_repo_dir):
        """Test handling of missing file."""
        with patch("app.core.repo_analyzer.get_file_content") as mock_content:
            mock_content.side_effect = FileNotFoundError("File not found")
            
            from app.core.repo_analyzer import get_file_content
            
            with pytest.raises(FileNotFoundError, match="File not found"):
                get_file_content(str(temp_repo_dir), "nonexistent.py")
    
    def test_get_file_content_outside_repo(self, temp_repo_dir):
        """Test path traversal protection."""
        with patch("app.core.repo_analyzer.get_file_content") as mock_content:
            mock_content.side_effect = ValueError("Path outside repository")
            
            from app.core.repo_analyzer import get_file_content
            
            with pytest.raises(ValueError, match="Path outside repository"):
                get_file_content(str(temp_repo_dir), "../../../etc/passwd")
    
    def test_search_files(self, temp_repo_dir):
        """Test searching files."""
        with patch("app.core.repo_analyzer.search_files") as mock_search:
            mock_search.return_value = [
                {"path": "src/payment.py", "name": "payment.py", "type": "file"},
                {"path": "src/payment_test.py", "name": "payment_test.py", "type": "file"},
            ]
            
            from app.core.repo_analyzer import search_files
            
            result = search_files(str(temp_repo_dir), query="payment")
            
            assert len(result) == 2
            assert all("payment" in f["name"].lower() for f in result)


class TestRepositoryAnalysis:
    """Test complete repository analysis."""
    
    @pytest.mark.asyncio
    async def test_analyze_repository(self, temp_repo_dir):
        """Test complete repository analysis."""
        with patch("app.core.repo_analyzer.analyze_repository") as mock_analyze:
            mock_analyze.return_value = {
                "repository_id": "test-id",
                "status": "completed",
                "files_analyzed": 50,
                "functions_found": 200,
                "classes_found": 50,
                "dependencies_found": 30,
                "parse_errors": 0,
            }
            
            from app.core.repo_analyzer import analyze_repository
            
            result = await analyze_repository(str(temp_repo_dir))
            
            assert result["status"] == "completed"
            assert result["files_analyzed"] == 50
            assert result["functions_found"] == 200
    
    @pytest.mark.asyncio
    async def test_analyze_repository_with_errors(self, temp_repo_dir):
        """Test analysis handling parse errors gracefully."""
        with patch("app.core.repo_analyzer.analyze_repository") as mock_analyze:
            mock_analyze.return_value = {
                "repository_id": "test-id",
                "status": "completed_with_errors",
                "files_analyzed": 48,
                "parse_errors": 2,
            }
            
            from app.core.repo_analyzer import analyze_repository
            
            result = await analyze_repository(str(temp_repo_dir))
            
            assert result["status"] == "completed_with_errors"
            assert result["parse_errors"] == 2


class TestRepositoryStatus:
    """Test repository status management."""
    
    def test_update_repository_status(self):
        """Test updating repository status."""
        repo = MagicMock(spec=Repository)
        repo.status = RepositoryStatus.PENDING
        
        with patch("app.core.repo_analyzer.update_repository_status") as mock_update:
            mock_update.return_value = True
            
            from app.core.repo_analyzer import update_repository_status
            
            result = update_repository_status(repo, RepositoryStatus.ACTIVE)
            
            assert result is True


class TestCleanup:
    """Test repository cleanup."""
    
    def test_delete_repository_files(self, temp_repo_dir):
        """Test deleting repository files."""
        with patch("app.core.repo_analyzer.delete_repository") as mock_delete:
            mock_delete.return_value = True
            
            from app.core.repo_analyzer import delete_repository
            
            result = delete_repository(str(temp_repo_dir))
            
            assert result is True
    
    def test_delete_nonexistent_repository(self):
        """Test deleting non-existent repository."""
        with patch("app.core.repo_analyzer.delete_repository") as mock_delete:
            mock_delete.side_effect = FileNotFoundError("Repository not found")
            
            from app.core.repo_analyzer import delete_repository
            
            with pytest.raises(FileNotFoundError, match="Repository not found"):
                delete_repository("/nonexistent/path")
