"""Completion command for generating shell completions."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


class Shell(str, Enum):
    """Supported shells for completion."""

    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    POWERSHELL = "powershell"


def get_completion_script(shell: Shell) -> str:
    """Generate the completion script for the specified shell.

    Args:
        shell: The shell type

    Returns:
        The completion script content
    """
    # Typer/Click uses a specific format for completion scripts
    # We leverage Typer's built-in completion support

    if shell == Shell.BASH:
        return '''# dtctl bash completion
# Add this to your ~/.bashrc or ~/.bash_profile:
#   eval "$(dtctl completion bash)"
# Or save to a file:
#   dtctl completion bash > /etc/bash_completion.d/dtctl

_dtctl_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   _DTCTL_COMPLETE=bash_complete $1 ) )
    return 0
}

complete -o default -F _dtctl_completion dtctl
'''

    elif shell == Shell.ZSH:
        return '''#compdef dtctl
# dtctl zsh completion
# Add this to your ~/.zshrc:
#   eval "$(dtctl completion zsh)"
# Or save to a file in your fpath:
#   dtctl completion zsh > ~/.zfunc/_dtctl

_dtctl() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[dtctl] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _DTCTL_COMPLETE=zsh_complete dtctl)}")

    for key descr in ${(kv)response}; do
        if [[ "$descr" == "_" ]]; then
            completions+=("$key")
        else
            completions_with_descriptions+=("$key":"$descr")
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _dtctl dtctl
'''

    elif shell == Shell.FISH:
        return '''# dtctl fish completion
# Add this to your ~/.config/fish/completions/dtctl.fish:
#   dtctl completion fish > ~/.config/fish/completions/dtctl.fish

function _dtctl_completion
    set -l response (env _DTCTL_COMPLETE=fish_complete COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) dtctl)

    for completion in $response
        set -l metadata (string split "," -- $completion)

        if [ $metadata[1] != "_" ]
            echo -e $metadata[1]\\t$metadata[2]
        else
            echo -e $metadata[2]
        end
    end
end

complete --no-files --command dtctl --arguments "(_dtctl_completion)"
'''

    elif shell == Shell.POWERSHELL:
        return '''# dtctl PowerShell completion
# Add this to your PowerShell profile:
#   dtctl completion powershell | Out-String | Invoke-Expression
# Or save to a file and dot-source it

Register-ArgumentCompleter -Native -CommandName dtctl -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $env:COMP_WORDS = $commandAst.ToString()
    $env:COMP_CWORD = $commandAst.CommandElements.Count - 1
    $env:_DTCTL_COMPLETE = "powershell_complete"
    dtctl | ForEach-Object {
        $completion = $_ -Split ","
        if ($completion[0] -eq "_") {
            [System.Management.Automation.CompletionResult]::new($completion[1])
        } else {
            [System.Management.Automation.CompletionResult]::new($completion[1], $completion[1], 'ParameterValue', $completion[0])
        }
    }
    $env:_DTCTL_COMPLETE = $null
}
'''

    return ""


@app.callback(invoke_without_command=True)
def generate_completion(
    ctx: typer.Context,
    shell: Shell = typer.Argument(..., help="Shell type (bash, zsh, fish, powershell)"),
    install: bool = typer.Option(
        False,
        "--install",
        "-i",
        help="Install the completion to your shell config",
    ),
) -> None:
    """Generate shell completion scripts.

    Generates completion scripts for bash, zsh, fish, or PowerShell.
    These scripts enable tab-completion for dtctl commands and options.

    Examples:
        # Print completion script to stdout
        dtctl completion bash

        # Add to your shell config
        eval "$(dtctl completion bash)"

        # Save to a file
        dtctl completion zsh > ~/.zfunc/_dtctl

        # Install automatically (experimental)
        dtctl completion bash --install
    """
    if ctx.invoked_subcommand is not None:
        return

    script = get_completion_script(shell)

    if install:
        _install_completion(shell, script)
    else:
        # Print to stdout for piping/redirection
        print(script)


def _install_completion(shell: Shell, script: str) -> None:
    """Install the completion script to the appropriate location.

    Args:
        shell: The shell type
        script: The completion script content
    """
    home = Path.home()

    if shell == Shell.BASH:
        # Try common locations
        rc_files = [
            home / ".bashrc",
            home / ".bash_profile",
        ]
        completion_dir = Path("/etc/bash_completion.d")

        if completion_dir.exists() and completion_dir.is_dir():
            target = completion_dir / "dtctl"
            try:
                target.write_text(script)
                console.print(f"[green]Installed completion to {target}[/green]")
                return
            except PermissionError:
                console.print(f"[yellow]Permission denied writing to {target}[/yellow]")

        # Fall back to RC file
        for rc_file in rc_files:
            if rc_file.exists():
                line = '\neval "$(dtctl completion bash)"\n'
                content = rc_file.read_text()
                if "dtctl completion" not in content:
                    with open(rc_file, "a") as f:
                        f.write(line)
                    console.print(f"[green]Added completion to {rc_file}[/green]")
                    console.print("[dim]Restart your shell or run: source ~/.bashrc[/dim]")
                else:
                    console.print(f"[yellow]Completion already in {rc_file}[/yellow]")
                return

        console.print("[red]Could not find a suitable location for bash completion[/red]")

    elif shell == Shell.ZSH:
        zshrc = home / ".zshrc"
        zfunc = home / ".zfunc"

        # Create zfunc directory if it doesn't exist
        zfunc.mkdir(exist_ok=True)
        target = zfunc / "_dtctl"
        target.write_text(script)
        console.print(f"[green]Installed completion to {target}[/green]")

        # Ensure zfunc is in fpath
        if zshrc.exists():
            content = zshrc.read_text()
            if "fpath=(~/.zfunc" not in content and '.zfunc' not in content:
                with open(zshrc, "a") as f:
                    f.write('\nfpath=(~/.zfunc $fpath)\nautoload -Uz compinit && compinit\n')
                console.print(f"[green]Added fpath to {zshrc}[/green]")
        console.print("[dim]Restart your shell or run: source ~/.zshrc[/dim]")

    elif shell == Shell.FISH:
        fish_completions = home / ".config" / "fish" / "completions"
        fish_completions.mkdir(parents=True, exist_ok=True)
        target = fish_completions / "dtctl.fish"
        target.write_text(script)
        console.print(f"[green]Installed completion to {target}[/green]")
        console.print("[dim]Completions will be available in new fish sessions[/dim]")

    elif shell == Shell.POWERSHELL:
        # PowerShell profile location varies
        console.print("[yellow]PowerShell completion installation:[/yellow]")
        console.print("Add the following to your PowerShell profile:")
        console.print("[dim]dtctl completion powershell | Out-String | Invoke-Expression[/dim]")
        console.print("\nTo find your profile path, run: $PROFILE")
