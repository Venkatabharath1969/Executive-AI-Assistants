"""
NOVA Voice AI Assistant — One-time setup script.

Installs the required Python dependencies and fetches Playwright browser binaries
for web automation.
"""
import platform
import subprocess
import sys
from pathlib import Path

OS = platform.system()  # "Windows" | "Darwin" | "Linux"
HERE = Path(__file__).resolve().parent

MIN_PY = (3, 11)
MAX_PY = (3, 13)


def _run(label: str, args: list[str]) -> None:
    print(f"\n▶ {label}")
    subprocess.run(args, check=True)


def _check_python() -> None:
    """Validate Python runtime version."""
    v = sys.version_info[:2]
    if v > MAX_PY:
        print(f"\n⚠️  Python {v[0]}.{v[1]} detected (tested on {MAX_PY[0]}.{MAX_PY[1]}). Continuing...")
        return
    if v < MIN_PY:
        print(f"\n❌ Python {v[0]}.{v[1]} detected — NOVA requires at least Python {MIN_PY[0]}.{MIN_PY[1]}.")
        sys.exit(1)


def main() -> None:
    print(f"⚙  NOVA Setup — detected OS: {OS or 'unknown'}, Python {sys.version_info[0]}.{sys.version_info[1]}")
    _check_python()

    # Install dependencies
    _run("Installing Python dependencies...",
         [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Playwright browser binaries
    try:
        _run("Installing Playwright browser engine (chromium)...",
             [sys.executable, "-m", "playwright", "install", "chromium"])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\n⚠️  Playwright browser installation skipped or encountered an error ({e}).")
        print("    You can install it later with: python -m playwright install chromium")

    print("\n✅ Setup complete!")
    print("   1) Configure your environment in .env (GEMINI_API_KEY, Microsoft Graph / WorkIQ credentials)")
    print("   2) Run: python main.py")
    print("   3) Speak or type to interact with NOVA.")


if __name__ == "__main__":
    main()
