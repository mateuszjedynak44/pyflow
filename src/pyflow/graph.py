
from heapq import heappop, heappush

from pyflow.models import Workflow, WorkflowValidationError


def topological_order(workflow: Workflow) -> list[str]:
    """Return task names in deterministic topological order."""
    tasks = workflow.tasks

    in_degree = {
        name: len(task.dependencies)
        for name, task in tasks.items()
    }

    dependents: dict[str, list[str]] = {
        name: [] for name in tasks
    }

    for name, task in tasks.items():
        for dependency in task.dependencies:
            if dependency not in tasks:
                raise WorkflowValidationError(
                    f"Task '{name}' has unknown dependency "
                    f"'{dependency}'."
                )
            dependents[dependency].append(name)

    ready: list[str] = []

    for name, degree in in_degree.items():
        if degree == 0:
            heappush(ready, name)

    result: list[str] = []

    while ready:
        name = heappop(ready)
        result.append(name)

        for dependent in sorted(dependents[name]):
            in_degree[dependent] -= 1

            if in_degree[dependent] == 0:
                heappush(ready, dependent)

    if len(result) != len(tasks):
        raise WorkflowValidationError(
            "Workflow contains a dependency cycle."
        )

    return result


def execution_layers(workflow: Workflow) -> list[list[str]]:
    """Group tasks into deterministic parallel execution layers."""
    order = topological_order(workflow)
    tasks = workflow.tasks
    completed: set[str] = set()
    layers: list[list[str]] = []

    while len(completed) < len(order):
        layer = sorted(
            name
            for name in order
            if name not in completed
            and tasks[name].dependencies <= completed
        )

        if not layer:
            raise WorkflowValidationError(
                "Workflow contains a dependency cycle."
            )

        layers.append(layer)
        completed.update(layer)

    return layers
