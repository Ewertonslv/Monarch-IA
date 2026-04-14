import pytest
import asyncio
from core.circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitState


@pytest.mark.asyncio
async def test_circuit_starts_closed():
    cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout=60)
    assert cb.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_success_keeps_circuit_closed():
    cb = CircuitBreaker("test", failure_threshold=3)

    async def ok():
        return "ok"

    result = await cb.call(ok)
    assert result == "ok"
    assert cb.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_failures_open_circuit():
    cb = CircuitBreaker("test", failure_threshold=3)

    async def fail():
        raise ValueError("boom")

    for _ in range(3):
        with pytest.raises(ValueError):
            await cb.call(fail)

    assert cb.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_open_circuit_rejects_calls():
    cb = CircuitBreaker("test", failure_threshold=2)

    async def fail():
        raise ValueError("boom")

    for _ in range(2):
        with pytest.raises(ValueError):
            await cb.call(fail)

    async def ok():
        return "ok"

    with pytest.raises(CircuitBreakerError):
        await cb.call(ok)


@pytest.mark.asyncio
async def test_circuit_recovers_after_timeout():
    cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.1)

    async def fail():
        raise ValueError("boom")

    for _ in range(2):
        with pytest.raises(ValueError):
            await cb.call(fail)

    assert cb.state == CircuitState.OPEN
    await asyncio.sleep(0.15)
    assert cb.state == CircuitState.HALF_OPEN


@pytest.mark.asyncio
async def test_success_in_half_open_closes_circuit():
    cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.1)

    async def fail():
        raise ValueError("boom")

    async def ok():
        return "good"

    for _ in range(2):
        with pytest.raises(ValueError):
            await cb.call(fail)

    await asyncio.sleep(0.15)
    result = await cb.call(ok)
    assert result == "good"
    assert cb.state == CircuitState.CLOSED
