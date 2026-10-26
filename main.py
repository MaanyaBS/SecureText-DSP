"""SecureText entry point.  Run with:  python main.py"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print(
            "Tkinter is not available in this Python installation.\n"
            "Windows: re-run the Python installer and tick 'tcl/tk and IDLE'.\n"
            "Ubuntu/Debian: sudo apt install python3-tk\n"
            "macOS (Homebrew): brew install python-tk"
        )
        return 1
    try:
        import cryptography  # noqa: F401
    except ImportError:
        print("The 'cryptography' package is missing. Run: python -m pip install -r requirements.txt")
        return 1

    from gui.main_window import run

    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
