from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)  # type: ignore[name-defined]

_root = Path(__file__).resolve().parent.parent
_src_pkg = _root / "src" / "faq_bench"
if _src_pkg.is_dir():
    __path__.append(str(_src_pkg))
