"""One-time bootstrap: installs missing dependencies and makes sure an API key is available.

Runs automatically when the app starts, so there's no manual venv/pip-install/.env
step required before the first `python app.py`. Deliberately has zero third-party
imports at module load time, so it can run before those packages exist.
"""
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_PATH = os.path.join(_ROOT, ".env")
_REQUIRED_MODULES = ["flask", "openai", "dotenv"]


def ensure_dependencies():
    missing = [pkg for pkg in _REQUIRED_MODULES if not _is_importable(pkg)]
    if not missing:
        return
    print(f"Installing missing dependencies: {', '.join(missing)}...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r",
        os.path.join(_ROOT, "requirements.txt"),
    ])


def _is_importable(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def ensure_api_key():
    from dotenv import load_dotenv, set_key

    load_dotenv(_ENV_PATH)
    if os.environ.get("OPENAI_API_KEY"):
        return

    print("No OpenAI API key found.")
    try:
        from getpass import getpass
        api_key = getpass("Paste your OpenAI API key (input hidden, get one at platform.openai.com/api-keys): ").strip()
    except Exception:
        api_key = input("Paste your OpenAI API key: ").strip()

    if not api_key:
        print("No key entered. The app will start, but requests to the model will fail until OPENAI_API_KEY is set.")
        return

    os.environ["OPENAI_API_KEY"] = api_key
    if not os.path.exists(_ENV_PATH):
        open(_ENV_PATH, "a").close()
    set_key(_ENV_PATH, "OPENAI_API_KEY", api_key)
    print(f"Saved to {_ENV_PATH} — you won't be asked again.")
