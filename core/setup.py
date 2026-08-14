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
    if os.environ.get("GROQ_API_KEY"):
        return

    if not sys.stdin.isatty():
        # Non-interactive environment (a hosting platform's build/run step) -
        # the key has to already be set as an env var there, since there's no
        # terminal to prompt into.
        raise RuntimeError(
            "GROQ_API_KEY is not set. Set it as an environment variable in your "
            "hosting provider's dashboard (get a free key at https://console.groq.com/keys)."
        )

    print("No Groq API key found.")
    try:
        from getpass import getpass
        api_key = getpass("Paste your Groq API key (input hidden, get a free one at console.groq.com/keys): ").strip()
    except Exception:
        api_key = input("Paste your Groq API key: ").strip()

    if not api_key:
        print("No key entered. The app will start, but requests to the model will fail until GROQ_API_KEY is set.")
        return

    os.environ["GROQ_API_KEY"] = api_key
    if not os.path.exists(_ENV_PATH):
        open(_ENV_PATH, "a").close()
    set_key(_ENV_PATH, "GROQ_API_KEY", api_key)
    print(f"Saved to {_ENV_PATH} — you won't be asked again.")
