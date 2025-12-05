"""Allocation domain package."""

from app.domain.allocation.rules import AllocationRules
from app.domain.allocation.naming import NamingConvention

__all__ = ["AllocationRules", "NamingConvention"]
