import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # failing, rejecting calls
    HALF_OPEN = "half_open" # testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when a call is rejected because the circuit is open."""


class CircuitBreaker:
    """Simple per-agent circuit breaker.

    Transitions:
      CLOSED  → OPEN       when failure_threshold consecutive failures occur
      OPEN    → HALF_OPEN  after recovery_timeout seconds
      HALF_OPEN → CLOSED   on first success
      HALF_OPEN → OPEN     on any failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if self._opened_at and (time.monotonic() - self._opened_at) >= self.recovery_timeout:
                logger.info("[%s] Circuit transitioning OPEN → HALF_OPEN", self.name)
                self._state = CircuitState.HALF_OPEN
        return self._state

    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            logger.info("[%s] Circuit CLOSED after successful probe", self.name)
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None

    def _on_failure(self) -> None:
        self._failure_count += 1
        if self._state == CircuitState.HALF_OPEN or self._failure_count >= self.failure_threshold:
            logger.warning("[%s] Circuit OPEN after %d failures", self.name, self._failure_count)
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()

    async def call(
        self,
        coro_fn: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"Circuit '{self.name}' is OPEN — call rejected. "
                f"Retry after {self.recovery_timeout}s."
            )
        try:
            result = await coro_fn(*args, **kwargs)
            self._on_success()
            return result
        except CircuitBreakerError:
            raise
        except Exception as exc:
            self._on_failure()
            raise exc
