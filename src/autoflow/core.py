"""Core flow primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter, sleep
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Union

from .errors import StepFailedError


FlowContext = Dict[str, Any]
StepCallable = Callable[[FlowContext], Any]


@dataclass(frozen=True)
class FlowEvent:
    """A single observable event emitted during a flow run."""

    name: str
    step: str
    elapsed: float = 0.0
    attempt: int = 1
    error: Optional[BaseException] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FlowResult:
    """The final result of a flow execution."""

    context: FlowContext
    events: List[FlowEvent] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)

    @property
    def elapsed(self) -> float:
        return sum(event.elapsed for event in self.events if event.name == "step_finished")

    def events_named(self, name: str) -> List[FlowEvent]:
        return [event for event in self.events if event.name == name]


@dataclass(frozen=True)
class Step:
    """A named unit of work inside a flow."""

    func: StepCallable
    name: str
    retries: int = 0
    delay: float = 0.0

    def __post_init__(self) -> None:
        if not callable(self.func):
            raise TypeError("step func must be callable")
        if not self.name:
            raise ValueError("step name must not be empty")
        if self.retries < 0:
            raise ValueError("retries must be zero or greater")
        if self.delay < 0:
            raise ValueError("delay must be zero or greater")

    def run(self, context: FlowContext, events: List[FlowEvent]) -> None:
        max_attempts = self.retries + 1

        for attempt in range(1, max_attempts + 1):
            started = perf_counter()
            events.append(FlowEvent("step_started", self.name, attempt=attempt))

            try:
                value = self.func(context)
                self._merge_result(context, value)
            except BaseException as exc:
                elapsed = perf_counter() - started
                events.append(
                    FlowEvent(
                        "step_failed",
                        self.name,
                        elapsed=elapsed,
                        attempt=attempt,
                        error=exc,
                    )
                )

                if attempt == max_attempts:
                    raise StepFailedError(self.name, exc, attempts=attempt, events=list(events)) from exc

                events.append(
                    FlowEvent(
                        "step_retrying",
                        self.name,
                        attempt=attempt,
                        metadata={"next_attempt": attempt + 1, "delay": self.delay},
                    )
                )
                if self.delay > 0:
                    sleep(self.delay)
                continue

            elapsed = perf_counter() - started
            events.append(FlowEvent("step_finished", self.name, elapsed=elapsed, attempt=attempt))
            return

    @staticmethod
    def _merge_result(context: FlowContext, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, Mapping):
            context.update(value)
            return
        context["_"] = value


class Flow:
    """Composable sequence of automation steps."""

    def __init__(self, name: str = "flow", steps: Optional[Iterable[Step]] = None) -> None:
        if not name:
            raise ValueError("flow name must not be empty")
        self.name = name
        self._steps = list(steps or [])

    @property
    def steps(self) -> List[Step]:
        return list(self._steps)

    def add(
        self,
        item: Union[Step, StepCallable],
        *,
        name: Optional[str] = None,
        retries: int = 0,
        delay: float = 0.0,
    ) -> "Flow":
        next_step = item if isinstance(item, Step) else step(name=name, retries=retries, delay=delay)(item)
        return Flow(self.name, [*self._steps, next_step])

    def run(self, initial: Optional[Mapping[str, Any]] = None) -> FlowResult:
        if initial is not None and not isinstance(initial, Mapping):
            raise TypeError("initial context must be a mapping")

        context: FlowContext = dict(initial or {})
        events = [FlowEvent("flow_started", self.name, metadata={"steps": len(self._steps)})]
        started = perf_counter()

        try:
            for item in self._steps:
                item.run(context, events)
        except StepFailedError as exc:
            elapsed = perf_counter() - started
            events.append(FlowEvent("flow_failed", self.name, elapsed=elapsed, error=exc))
            exc.events = list(events)
            raise

        elapsed = perf_counter() - started
        events.append(FlowEvent("flow_finished", self.name, elapsed=elapsed))
        return FlowResult(context=context, events=events)


def step(
    func: Optional[Union[StepCallable, str]] = None,
    *,
    name: Optional[str] = None,
    retries: int = 0,
    delay: float = 0.0,
) -> Union[Callable[[StepCallable], Step], Step]:
    """Wrap a callable as a flow step."""

    if retries < 0:
        raise ValueError("retries must be zero or greater")
    if delay < 0:
        raise ValueError("delay must be zero or greater")
    if isinstance(func, str):
        if name is not None:
            raise ValueError("step name was provided twice")
        name = func
        func = None
    if func is not None and not callable(func):
        raise TypeError("step expects a callable or a step name")

    def decorator(func: StepCallable) -> Step:
        return Step(func=func, name=name or func.__name__, retries=retries, delay=delay)

    if callable(func):
        return decorator(func)

    return decorator
