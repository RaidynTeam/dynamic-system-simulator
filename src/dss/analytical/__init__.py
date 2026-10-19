"""Analytical classification and the critical-damping response solver."""

from .classification import classify_case, classify_roots
from .solver import solve_analytical

__all__ = ["classify_case", "classify_roots", "solve_analytical"]
