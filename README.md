# PyFlow

PyFlow is a Python library for defining, validating, planning and executing data workflows.

The project allows users to create tasks, define dependencies between them, validate a directed acyclic graph (DAG), plan execution order and execute the entire workflow synchronously.

## Requirements

- Python 3.11 or newer
- Git
- pytest

## Project structure

```text
pyflow/
|
|-- src/
|   |-- pyflow/
|       |-- __init__.py
|       |-- models.py
|       |-- graph.py
|       |-- execution.py
|
|-- tests/
|   |-- test_models.py
|   |-- test_graph.py
|   |-- test_execution.py
|
|-- examples/
|   |-- data/
|   |   |-- sales.csv
|   |-- run_example.py
|
|-- pyproject.toml
|-- README.md
```

## Installation

Clone the repository and enter the project directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the package:

```bash
python -m pip install -e ".[dev]"
```

## Features

- Task model based on dataclasses
- Workflow model for managing tasks
- Task dependency management
- DAG validation
- Detection of missing dependencies and cycles
- Deterministic topological sorting
- Execution layers
- Synchronous workflow execution
- Result passing between dependent tasks
- Task execution status tracking
- Error handling and dependency skipping
- Execution time measurement
- Text execution report
- Automated unit and integration tests

## Task and Workflow models

Each task contains:

- name - unique task identifier
- function - function executed by the engine
- dependencies - set of direct dependencies
- params - task configuration parameters
- description - optional task description

Task functions use the following interface:

```python
def task_function(inputs, params):
    return result
```

The inputs argument contains results from direct dependencies.

The params argument contains task configuration.

The Workflow class stores tasks and validates the workflow definition.

## Graph planning

PyFlow uses topological sorting based on Kahn's algorithm.

The algorithm determines a valid execution order while ensuring that every task is executed after its dependencies.

When multiple tasks are available, alphabetical ordering ensures deterministic results.

The time complexity of the heap-based implementation is:

O((V + E) log V)

Where:
- V is the number of tasks
- E is the number of dependencies

Execution layers group tasks whose dependencies have already been satisfied.

## Synchronous execution engine

The execution engine is implemented in execution.py.

The main public function is:

```python
from pyflow import run

result = run(workflow)
```

The RunResult object contains:

- outputs - mapping of task names to their results
- task_states - execution state of every task
- succeeded - indicates whether the entire workflow succeeded
- duration - total workflow execution time

## Task statuses

Every task has one of the following statuses:

| Status | Description |
|--------|-------------|
| PENDING | Task is waiting for execution |
| RUNNING | Task is currently executing |
| SUCCEEDED | Task completed successfully |
| FAILED | Task execution failed |
| SKIPPED | Task was skipped because a dependency failed |

## Error handling policy

PyFlow uses a policy that allows independent tasks to continue after an execution failure.

When a task fails:

1. The task receives the FAILED status.
2. Dependent tasks receive the SKIPPED status.
3. Independent tasks continue executing.
4. The engine raises TaskExecutionError after processing the workflow.

TaskExecutionError contains the failed task name, the original exception and the execution report.

The original exception is preserved using exception chaining.

## Execution time report

The engine measures execution time using time.perf_counter().

The report contains:
- Name of each task
- Task execution status
- Individual execution time
- Total workflow execution time
- Overall execution result

## Example workflow

The project includes an end-to-end example:

CSV -> Data cleaning -> Aggregation -> JSON

The example reads a local CSV file, validates records, calculates statistics and generates a JSON report.

Run the example:

```bash
python examples/run_example.py
```

The generated report is saved in:

```text
examples/report.json
```

## Running tests

Run all automated tests:

```bash
python -m pytest -v
```

The tests cover:
- Empty workflows
- Single tasks
- Task dependencies
- Duplicate tasks
- Missing dependencies
- Cycles
- Deterministic execution order
- Execution layers
- Result passing
- Task parameters
- Execution failures
- Skipped dependent tasks
- Independent task execution
- Execution time measurement

## Public API

The main public API is available directly from the pyflow package:

```python
from pyflow import (
    Task,
    Workflow,
    WorkflowValidationError,
    TaskStatus,
    TaskState,
    RunResult,
    TaskExecutionError,
    topological_order,
    execution_layers,
    run,
)
```

## Development

The project is developed using Python 3.11+.

The implementation separates:
- Models - task and workflow definitions
- Graph - DAG validation and execution planning
- Execution - synchronous workflow execution and reporting

All changes are covered by automated tests.
