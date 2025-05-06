# Install Deno documentation tools
# This command installs the Deno CLI documentation tools globally
# deno install docs
deno install -A -f -n docs https://deno.land/x/deno_docs/cli.ts

# Install uv documentation tools
# This command installs the documentation tools for uv
# uv is a Python package installer and resolver, similar to pip
# The 'docs' package will be installed in the current environment
uv install docs

# Generate documentation
uv docs

# Install pre-commit documentation tools
# This command installs the documentation tools for pre-commit
# pre-commit is a framework for managing and maintaining multi-language pre-commit hooks
pre-commit install docs

# linting (mypy is essentially a python linter on steroids)
uv run mypy test.py



