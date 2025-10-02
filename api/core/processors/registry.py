"""Processor registry initialization and management."""

from .base import registry
from .us import BOFAProcessor, ChaseProcessor, AmexProcessor


def init_processors():
    """Initialize and register all bank processors.

    This function should be called during application startup.
    """
    # Register US processors
    registry.register(BOFAProcessor())
    registry.register(ChaseProcessor())
    registry.register(AmexProcessor())

    # Future: Add Chinese bank processors
    # from .cn import ICBCProcessor, CCBProcessor
    # registry.register(ICBCProcessor())
    # registry.register(CCBProcessor())

    return registry


def get_processor_registry():
    """Get the initialized processor registry.

    Returns:
        ProcessorRegistry instance with all processors registered
    """
    return registry


# Auto-initialize on import
init_processors()
