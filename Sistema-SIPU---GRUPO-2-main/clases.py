"""Wrapper compatible hacia `sipu.models`.

Este archivo actúa como adaptador para mantener compatibilidad con
scripts que importen `clases` desde la raíz. Internamente delega
en `sipu.models` (la nueva ubicación).
"""

from sipu.models import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("__")]





