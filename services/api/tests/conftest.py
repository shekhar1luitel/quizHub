from __future__ import annotations

import sys
from pathlib import Path

import sqlalchemy.orm as orm

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_original_sessionmaker = orm.sessionmaker


def _sessionmaker_with_defaults(*args, **kwargs):
    kwargs.setdefault("expire_on_commit", False)
    return _original_sessionmaker(*args, **kwargs)


orm.sessionmaker = _sessionmaker_with_defaults
