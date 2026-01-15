# Backend Setup (Python 3.12 + uv)

This project uses:

- **Python >= 3.12**
- **uv** for dependency management (creates a local `.venv/`)
- **uv.lock** for reproducible installs

## Requirements

- Ubuntu 22.04
- Python **3.12+**
- uv installed for your user

---

## 1. Check your Python version

```bash
python3.12 --version
```

If you see `Python 3.12.x`, you’re good to go.

If `python3.12` is not found, install it using the steps below.

---

## 2. Install Python 3.12 (Ubuntu 22.04)

Do **not** change Ubuntu’s system `python3`. Install 3.12 alongside it.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

Verify:

```bash
python3.12 --version
```

---

## 3. Install uv (per-user)

Install uv for your user (no sudo):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify:

```bash
uv --version
```

### If `uv` command is not found

Add uv to your PATH (choose the one you use):

**zsh**

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**bash**

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify again:

```bash
uv --version
```

---

## 4. Install project dependencies (from lockfile) and register git hooks

From the repository root (where `pyproject.toml` and `uv.lock` exist):

```bash
uv venv --python python3.12
uv sync
uv run pre-commit install
```

This will:

- Create `./.venv/`
- Install exact versions from `uv.lock`

---

## 5. Run commands (example)

```bash
uv run python --version
```

(Use `uv run ...` for all Python/Django commands so the project venv is used.)
