
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any


TaskFunction = Callable[
    [Mapping[str, Any], Mapping[str, Any]],
    Any,
]


class WorkflowValidationError(ValueError):
    """Raised when a workflow definition is invalid."""


@dataclass(frozen=True)
class Task:
    name: str
    function: TaskFunction
    dependencies: frozenset[str] = field(default_factory=frozenset)
    params: Mapping[str, Any] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Task name cannot be empty.")

        if not callable(self.function):
            raise TypeError("Task function must be callable.")

        dependencies = frozenset(self.dependencies)

        if self.name in dependencies:
            raise ValueError(
                f"Task '{self.name}' cannot depend on itself."
            )

        if not isinstance(self.params, Mapping):
            raise TypeError("Task params must be a mapping.")

        object.__setattr__(self, "dependencies", dependencies)
        object.__setattr__(
            self,
            "params",
            MappingProxyType(dict(self.params)),
        )


class Workflow:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    @property
    def tasks(self) -> Mapping[str, Task]:
        return MappingProxyType(self._tasks)

    def add_task(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("Only Task instances can be added.")

        if task.name in self._tasks:
            raise ValueError(
                f"Task '{task.name}' is already registered."
            )

        self._tasks[task.name] = task

    def validate(self) -> None:
        for task in self._tasks.values():
            missing = task.dependencies - self._tasks.keys()

            if missing:
                names = ", ".join(sorted(missing))
                raise WorkflowValidationError(
                    f"Task '{task.name}' has unknown dependencies: {names}."
                )

        from pyflow.graph import topological_order

        topological_order(self)
