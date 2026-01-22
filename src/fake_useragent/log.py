"""Logging helpers used by the package.

Exposes a module-level ``logger`` configured with the package name.
"""
import logging

logger = logging.getLogger(__package__) 
