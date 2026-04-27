from __future__ import annotations

import argparse
import os
import platform
import sys
from pathlib import Path


def bundled_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    if os.environ.get("CAULOTI_DATA_DIR"):
        return Path(os.environ["CAULOTI_DATA_DIR"])
    system = platform.system().lower()
    if system == "windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    elif system == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "PuntoVentaCauloti"


def configure_environment(root: Path, storage: Path) -> None:
    storage.mkdir(parents=True, exist_ok=True)
    media = storage / "media"
    media.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cauloti_pos.settings")
    os.environ.setdefault("CAULOTI_DEBUG", "0")
    os.environ.setdefault("CAULOTI_ALLOWED_HOSTS", "127.0.0.1,localhost")
    os.environ.setdefault("CAULOTI_DB_PATH", str(storage / "db.sqlite3"))
    os.environ.setdefault("CAULOTI_MEDIA_ROOT", str(media))
    os.environ.setdefault("CAULOTI_SERVE_MEDIA", "1")
    sys.path.insert(0, str(root))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()

    root = bundled_root()
    configure_environment(root, data_dir())

    import django
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from waitress import serve

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)

    User = get_user_model()
    if not User.objects.exists():
        call_command("seed_demo", verbosity=0)

    from cauloti_pos.wsgi import application

    serve(application, host=args.host, port=args.port, threads=8)


if __name__ == "__main__":
    main()

