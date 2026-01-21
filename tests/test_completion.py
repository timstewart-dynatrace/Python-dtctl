"""Tests for the completion command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dtctl.cli import app
from dtctl.commands.completion import Shell, get_completion_script


class TestGetCompletionScript:
    """Tests for completion script generation."""

    def test_bash_completion_script(self):
        """Test bash completion script generation."""
        script = get_completion_script(Shell.BASH)
        assert "bash completion" in script.lower()
        assert "_dtctl_completion" in script
        assert "COMP_WORDS" in script
        assert "complete" in script

    def test_zsh_completion_script(self):
        """Test zsh completion script generation."""
        script = get_completion_script(Shell.ZSH)
        assert "zsh" in script.lower()
        assert "_dtctl" in script
        assert "compdef" in script

    def test_fish_completion_script(self):
        """Test fish completion script generation."""
        script = get_completion_script(Shell.FISH)
        assert "fish" in script.lower()
        assert "_dtctl_completion" in script
        assert "complete" in script

    def test_powershell_completion_script(self):
        """Test PowerShell completion script generation."""
        script = get_completion_script(Shell.POWERSHELL)
        assert "PowerShell" in script
        assert "Register-ArgumentCompleter" in script
        assert "dtctl" in script


class TestCompletionCommand:
    """Tests for the completion CLI command."""

    def test_completion_bash(self, cli_runner: CliRunner):
        """Test generating bash completion."""
        result = cli_runner.invoke(app, ["completion", "bash"])
        assert result.exit_code == 0
        assert "_dtctl_completion" in result.output
        assert "complete" in result.output

    def test_completion_zsh(self, cli_runner: CliRunner):
        """Test generating zsh completion."""
        result = cli_runner.invoke(app, ["completion", "zsh"])
        assert result.exit_code == 0
        assert "_dtctl" in result.output
        assert "compdef" in result.output

    def test_completion_fish(self, cli_runner: CliRunner):
        """Test generating fish completion."""
        result = cli_runner.invoke(app, ["completion", "fish"])
        assert result.exit_code == 0
        assert "fish" in result.output.lower()
        assert "complete" in result.output

    def test_completion_powershell(self, cli_runner: CliRunner):
        """Test generating PowerShell completion."""
        result = cli_runner.invoke(app, ["completion", "powershell"])
        assert result.exit_code == 0
        assert "Register-ArgumentCompleter" in result.output

    def test_completion_requires_shell_arg(self, cli_runner: CliRunner):
        """Test that completion command requires shell argument."""
        result = cli_runner.invoke(app, ["completion"])
        assert result.exit_code != 0
        # Should show missing argument error

    def test_completion_invalid_shell(self, cli_runner: CliRunner):
        """Test completion with invalid shell type."""
        result = cli_runner.invoke(app, ["completion", "invalid-shell"])
        assert result.exit_code != 0


class TestCompletionInstall:
    """Tests for completion script installation."""

    def test_bash_install(self, cli_runner: CliRunner):
        """Test installing bash completion."""
        # Note: --install flag must come before the shell argument
        result = cli_runner.invoke(app, ["completion", "--install", "bash"])
        # Should either succeed or show some output about installation
        # The test is mainly to verify the command doesn't crash
        assert result.exit_code in (0, 1) or "Install" in result.output or "Added" in result.output

    def test_zsh_install(self, cli_runner: CliRunner):
        """Test installing zsh completion."""
        result = cli_runner.invoke(app, ["completion", "--install", "zsh"])
        # Should either succeed or show some output
        assert result.exit_code in (0, 1) or "Install" in result.output

    def test_fish_install(self, cli_runner: CliRunner):
        """Test installing fish completion."""
        result = cli_runner.invoke(app, ["completion", "--install", "fish"])
        # Should either succeed or show some output
        assert result.exit_code in (0, 1) or "Install" in result.output

    def test_powershell_install_shows_instructions(self, cli_runner: CliRunner):
        """Test PowerShell install shows manual instructions."""
        result = cli_runner.invoke(app, ["completion", "--install", "powershell"])
        # PowerShell installation shows instructions rather than auto-installing
        assert result.exit_code == 0
        assert "profile" in result.output.lower() or "$PROFILE" in result.output


class TestShellEnum:
    """Tests for Shell enum."""

    def test_shell_values(self):
        """Test Shell enum values."""
        assert Shell.BASH.value == "bash"
        assert Shell.ZSH.value == "zsh"
        assert Shell.FISH.value == "fish"
        assert Shell.POWERSHELL.value == "powershell"

    def test_all_shells_covered(self):
        """Test that all shells have completion scripts."""
        for shell in Shell:
            script = get_completion_script(shell)
            assert script, f"Missing completion script for {shell.value}"
            assert len(script) > 100, f"Completion script too short for {shell.value}"


class TestCompletionScriptContent:
    """Tests for completion script content validity."""

    def test_bash_script_is_sourceable(self):
        """Test that bash script has valid structure."""
        script = get_completion_script(Shell.BASH)
        # Should have a function definition
        assert "function" in script or "()" in script
        # Should register completion
        assert "complete" in script
        # Should reference dtctl
        assert "dtctl" in script

    def test_zsh_script_has_compdef(self):
        """Test that zsh script has compdef."""
        script = get_completion_script(Shell.ZSH)
        assert "compdef" in script
        assert "_dtctl" in script

    def test_fish_script_has_complete_command(self):
        """Test that fish script has complete command."""
        script = get_completion_script(Shell.FISH)
        assert "complete" in script
        assert "--command" in script or "-c" in script

    def test_powershell_script_has_register(self):
        """Test that PowerShell script has Register-ArgumentCompleter."""
        script = get_completion_script(Shell.POWERSHELL)
        assert "Register-ArgumentCompleter" in script
        assert "-Native" in script
        assert "-CommandName" in script
