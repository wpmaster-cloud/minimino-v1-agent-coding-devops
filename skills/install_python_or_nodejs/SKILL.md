---
name: install_python_or_nodejs
description: "Install Python 3.12 or Node.js 22 in the workspace. Use when a mission requires Python or Node.js but they are not yet installed."
---

# Install Python or Node.js

Use this skill when the mission requires Python or Node.js and they are not available.

## Install Python 3.12

Run this exact sequence:

```bash
RELEASE_DATE="20260325"
PYTHON_VERSION="3.12.13"
PY_ARCH=$(uname -m)
case "$PY_ARCH" in
  aarch64|arm64) PY_ARCH="aarch64-unknown-linux-musl" ;;
  *)             PY_ARCH="x86_64-unknown-linux-musl" ;;
esac

FILENAME="cpython-${PYTHON_VERSION}+${RELEASE_DATE}-${PY_ARCH}-install_only.tar.gz"
DOWNLOAD_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE_DATE}/${FILENAME}"

curl -fsSL -o /tmp/python.tar.gz "$DOWNLOAD_URL"
mkdir -p /python
tar -xzf /tmp/python.tar.gz -C /python --strip-components=1
rm /tmp/python.tar.gz
export PATH="/python/bin:$PATH"
export PYTHONHOME="/python"
```

After install, verify with: `python3 --version`

To install pip packages: `python3 -m pip install <package>`

## Install Node.js 22

Run this exact sequence:

```bash
NODE_ARCH=$(uname -m)
case "$NODE_ARCH" in
  aarch64|arm64) NODE_ARCH="arm64" ;;
  *)             NODE_ARCH="x64" ;;
esac

curl -fsSL "https://nodejs.org/dist/v22.22.1/node-v22.22.1-linux-${NODE_ARCH}.tar.xz" | tar -xJ -C /usr/local --strip-components=1
```

After install, verify with: `node --version`

To install npm packages: `npm install <package>`

## Notes

- Python installs to `/python/bin/`. Make sure `PATH` includes `/python/bin`.
- Node.js installs to `/usr/local/bin/` (already in PATH).
- If Python or Node.js was installed in the background at startup (via `INSTALL_PYTHON` or `INSTALL_NODEJS` env vars), they may already be available — check first before installing.
