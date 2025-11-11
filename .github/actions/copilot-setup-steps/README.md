# Copilot Setup Steps

This composite action provides a standardized way to set up development environments in CI/CD workflows using [mise](https://mise.jdx.dev/).

## Features

- Installs and configures mise for managing runtime versions
- Supports Node.js, Ruby, and Python via mise
- Supports MoonBit toolchain installation
- Selective installation based on input parameters

## Usage

```yaml
- name: Setup environment
  uses: ./.github/actions/copilot-setup-steps
  with:
    setup-moonbit: 'true'  # Optional: Setup MoonBit toolchain
    setup-nodejs: 'true'    # Optional: Setup Node.js via mise
    setup-ruby: 'true'      # Optional: Setup Ruby via mise
    setup-python: 'true'    # Optional: Setup Python via mise
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `setup-moonbit` | Whether to setup MoonBit toolchain | No | `'false'` |
| `setup-nodejs` | Whether to setup Node.js | No | `'false'` |
| `setup-ruby` | Whether to setup Ruby | No | `'false'` |
| `setup-python` | Whether to setup Python | No | `'false'` |

## Tool Versions

Tool versions are defined in `.tool-versions` file at the repository root:

```
nodejs 20.18.0
ruby 3.3.6
python 3.12.7
```

## Examples

### Setup only MoonBit

```yaml
- uses: ./.github/actions/copilot-setup-steps
  with:
    setup-moonbit: 'true'
```

### Setup Node.js for testing

```yaml
- uses: ./.github/actions/copilot-setup-steps
  with:
    setup-nodejs: 'true'
```

### Setup multiple tools

```yaml
- uses: ./.github/actions/copilot-setup-steps
  with:
    setup-nodejs: 'true'
    setup-ruby: 'true'
    setup-python: 'true'
```

## How it works

1. **mise installation**: Installs mise CLI tool if any language runtime is requested
2. **Tool installation**: Uses mise to install tools based on `.tool-versions` file
3. **PATH configuration**: Adds mise shims directory to PATH for tool access
4. **MoonBit setup**: Separately installs MoonBit toolchain if requested

## Benefits

- **Consistent versions**: All language runtimes use versions from `.tool-versions`
- **Fast caching**: mise provides efficient caching of installed tools
- **Simplified maintenance**: Update versions in one place (`.tool-versions`)
- **Flexible**: Each job can request only what it needs
