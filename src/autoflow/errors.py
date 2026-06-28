"""Custom exceptions raised by autoflow."""

from __future__ import annotations


class AutoFlowError(Exception):
    """Base exception for autoflow."""


class StepFailedError(AutoFlowError):
    """Raised when a step fails after all retry attempts."""

    def __init__(
        self,
        step_name: str,
        original: BaseException,
        *,
        attempts: int = 1,
        events: object = None,
    ) -> None:
        super().__init__(f"step '{step_name}' failed: {original}")
        self.step_name = step_name
        self.original = original
        self.attempts = attempts
        self.events = events
