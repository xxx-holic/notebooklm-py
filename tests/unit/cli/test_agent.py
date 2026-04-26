"""Tests for agent CLI commands."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from notebooklm.notebooklm_cli import cli

from .conftest import get_cli_module

agent_module = get_cli_module("agent")
agent_templates_module = get_cli_module("agent_templates")


@pytest.fixture
def runner():
    return CliRunner()


class TestAgentShow:
    """Tests for agent show command."""

    def test_agent_show_codex_displays_content(self, runner):
        """Test that agent show codex displays the bundled instructions."""
        with patch.object(
            agent_module, "get_agent_source_content", return_value="# NotebookLM for Codex"
        ):
            result = runner.invoke(cli, ["agent", "show", "codex"])

        assert result.exit_code == 0
        assert "NotebookLM for Codex" in result.output

    def test_agent_show_claude_displays_content(self, runner):
        """Test that agent show claude displays the bundled instructions."""
        with patch.object(agent_module, "get_agent_source_content", return_value="# Claude Skill"):
            result = runner.invoke(cli, ["agent", "show", "claude"])

        assert result.exit_code == 0
        assert "Claude Skill" in result.output

    def test_agent_show_does_not_interpret_rich_markup(self, runner):
        """Test that Markdown brackets such as extras are printed literally."""
        content = 'pip install "notebooklm-py[browser,cookies] @ git+https://example"'
        with patch.object(agent_module, "get_agent_source_content", return_value=content):
            result = runner.invoke(cli, ["agent", "show", "codex"])

        assert result.exit_code == 0
        assert "notebooklm-py[browser,cookies]" in result.output

    def test_agent_show_missing_content_returns_error(self, runner):
        """Test error when bundled agent instructions are missing."""
        with patch.object(agent_module, "get_agent_source_content", return_value=None):
            result = runner.invoke(cli, ["agent", "show", "codex"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestAgentTemplates:
    """Tests for bundled agent template loading."""

    def test_codex_template_reads_repo_codex_guide_first(self, tmp_path):
        """Test that source checkouts prefer CODEX.md over AGENTS.md."""
        codex_guide = tmp_path / "CODEX.md"
        agents_guide = tmp_path / "AGENTS.md"
        codex_guide.write_text("# NotebookLM for Codex", encoding="utf-8")
        agents_guide.write_text("# Repository Guidelines", encoding="utf-8")

        with (
            patch.object(agent_templates_module, "REPO_ROOT_CODEX_GUIDE", codex_guide),
            patch.object(agent_templates_module, "REPO_ROOT_AGENTS", agents_guide),
        ):
            content = agent_templates_module.get_agent_source_content("codex")

        assert content is not None
        assert "NotebookLM for Codex" in content

    def test_codex_template_falls_back_to_package_data(self, tmp_path):
        """Test that codex content falls back to packaged data outside repo root."""
        with (
            patch.object(agent_templates_module, "REPO_ROOT_CODEX_GUIDE", tmp_path / "CODEX.md"),
            patch.object(agent_templates_module, "REPO_ROOT_AGENTS", tmp_path / "AGENTS.md"),
            patch.object(
                agent_templates_module,
                "_read_package_data",
                return_value="# NotebookLM for Codex",
            ),
        ):
            content = agent_templates_module.get_agent_source_content("codex")

        assert content is not None
        assert "NotebookLM for Codex" in content

    def test_claude_template_reads_package_data(self):
        """Test that claude content reads from packaged skill data."""
        content = agent_templates_module.get_agent_source_content("claude")

        assert content is not None
        assert "NotebookLM Automation" in content
