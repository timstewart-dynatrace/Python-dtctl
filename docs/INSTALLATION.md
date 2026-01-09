# Installing dtctl

> **⚠️ DISCLAIMER**: This tool is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use. Always test in non-production environments first.

This guide covers installing dtctl from source or PyPI.

## Prerequisites

- Python 3.10 or later
- pip (Python package installer)
- Git (for source installation)

## Installation Methods

### Option 1: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/python-dtctl.git
cd python-dtctl

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Verify the installation
dtctl --version
```

### Option 2: Install with pipx (Recommended for Users)

pipx installs Python applications in isolated environments:

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install dtctl
pipx install dtctl

# Verify
dtctl --version
```

### Option 3: Install with pip

```bash
# Install from PyPI (when published)
pip install dtctl

# Or install from source
pip install git+https://github.com/yourusername/python-dtctl.git

# Verify
dtctl --version
```

## Verify Installation

After installation, verify everything works:

```bash
# Check version
dtctl --version

# Show help
dtctl --help

# View available commands
dtctl get --help
dtctl query --help
```

## Shell Completion (Optional)

Enable tab completion for faster workflows.

### Bash

```bash
# Generate and install completion
dtctl --install-completion bash

# Or manually:
dtctl completion bash > ~/.dtctl-complete.bash
echo "source ~/.dtctl-complete.bash" >> ~/.bashrc
source ~/.bashrc
```

### Zsh

```bash
# Generate and install completion
dtctl --install-completion zsh

# Or manually:
mkdir -p ~/.zsh/completions
dtctl completion zsh > ~/.zsh/completions/_dtctl
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc
rm -f ~/.zcompdump*
source ~/.zshrc
```

### Fish

```bash
# Generate and install completion
dtctl --install-completion fish

# Or manually:
mkdir -p ~/.config/fish/completions
dtctl completion fish > ~/.config/fish/completions/dtctl.fish
```

## Updating dtctl

### From Source

```bash
cd python-dtctl
git pull
pip install -e .
```

### With pipx

```bash
pipx upgrade dtctl
```

### With pip

```bash
pip install --upgrade dtctl
```

## Uninstalling

### pipx

```bash
pipx uninstall dtctl
```

### pip

```bash
pip uninstall dtctl
```

### Remove Configuration (Optional)

```bash
# Linux
rm -rf ~/.config/dtctl

# macOS
rm -rf ~/Library/Application\ Support/dtctl

# Windows (PowerShell)
Remove-Item -Recurse $env:LOCALAPPDATA\dtctl
```

## Troubleshooting

### "command not found: dtctl"

The dtctl binary is not in your PATH. Check:

```bash
# Verify pip's bin directory is in PATH
python -m site --user-base
# Add the bin subdirectory to your PATH if needed
```

For pipx installations:
```bash
pipx ensurepath
# Then restart your shell
```

### "Permission denied"

You may need to use a virtual environment or install with `--user`:

```bash
pip install --user dtctl
```

### Python version issues

Ensure you're using Python 3.10+:

```bash
python --version
# or
python3 --version
```

If you have multiple Python versions, use the specific version:

```bash
python3.10 -m pip install dtctl
```

### Module import errors

Try reinstalling with all dependencies:

```bash
pip uninstall dtctl
pip install dtctl
```

## Next Steps

Now that dtctl is installed, see the [Quick Start Guide](QUICK_START.md) to learn how to:
- Configure your Dynatrace environment
- Execute commands
- Work with workflows, dashboards, DQL queries, and more

## Getting Help

- **Quick Start**: See [QUICK_START.md](QUICK_START.md) for usage examples
- **API Reference**: See [API_DESIGN.md](API_DESIGN.md) for complete command reference
- **Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md) for implementation details
- **Issues**: Report bugs at the GitHub repository
