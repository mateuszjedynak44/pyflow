from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any

from pyflow.graph import topological_order
from pyflow.models import Workflow


class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class TaskState:
    status: TaskStatus = TaskStatus.PENDING
    output: Any = None
    error: str | None = None
    started_at: float | None = None
    finished_at: float | None = None
    duration: float = 0.0


@dataclass
class RunResult:
    outputs: dict[str, Any] = field(default_factory=dict)
    task_states: dict[str, TaskState] = field(default_factory=dict)
    succeeded: bool = True
    duration: float = 0.0


class TaskExecutionError(RuntimeError):
    def __init__(self, task_name: str, original_error: Exception, result: RunResult):
        self.task_name = task_name
        self.original_error = original_error
        self.result = result
        super().__init__(
            f"Task '{task_name}' execution failed: {original_error}"
        )


def run(workflow: Workflow) -> RunResult:
    workflow.validate()

    result = RunResult(
        task_states={
            name: TaskState()
            for name in workflow.tasks
        }
    )

    workflow_start = perf_counter()
    first_failed_task = None
    first_error = None

    for task_name in topological_order(workflow):
        task = workflow.tasks[task_name]
        state = result.task_states[task_name]

        if any(
            result.task_states[dependency].status != TaskStatus.SUCCEEDED
            for dependency in task.dependencies
        ):
            state.status = TaskStatus.SKIPPED
            continue

        state.status = TaskStatus.RUNNING
        state.started_at = perf_counter()

        try:
            inputs = {
                dependency: result.outputs[dependency]
                for dependency in sorted(task.dependencies)
            }

            output = task.function(inputs, task.params)

            result.outputs[task_name] = output
            state.output = output
            state.status = TaskStatus.SUCCEEDED

        except Exception as exc:
            state.status = TaskStatus.FAILED
            state.error = str(exc)

            if first_error is None:
                first_error = exc
                first_failed_task = task_name

        finally:
            state.finished_at = perf_counter()
            state.duration = state.finished_at - state.started_at

    result.duration = perf_counter() - workflow_start
    result.succeeded = first_error is None

    if first_error is not None:
        raise TaskExecutionError(
            first_failed_task,
            first_error,
            result
        ) from first_error

    return result
