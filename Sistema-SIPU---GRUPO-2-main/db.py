"""Backward-compatible wrapper: reexporta `sipu.repository`.

Este fichero se mantiene en la raíz para compatibilidad con imports
existentes. Internamente delega en `sipu.repository.SQLiteRepository`.
"""

from sipu.repository import *  # noqa: F401,F403

__all__ = [
    name for name in dir() if not name.startswith("__")
]
