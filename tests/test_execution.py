import pytest

from pyflow.models import Task, Workflow
from pyflow.execution import (
    run,
    TaskStatus,
    TaskExecutionError,
)


def test_empty_workflow():
    workflow = Workflow()

    result = run(workflow)

    assert result.succeeded is True
    assert result.outputs == {}
    assert result.task_states == {}


def test_result_passing():
    workflow = Workflow()

    workflow.add_task(Task(
        name="first",
        function=lambda inputs, params: 10
    ))

    workflow.add_task(Task(
        name="second",
        function=lambda inputs, params: inputs["first"] + 5,
        dependencies=frozenset({"first"})
    ))

    result = run(workflow)

    assert result.outputs["first"] == 10
    assert result.outputs["second"] == 15


def test_parameters():
    workflow = Workflow()

    workflow.add_task(Task(
        name="calculate",
        function=lambda inputs, params: params["value"] * 2,
        params={"value": 10}
    ))

    result = run(workflow)

    assert result.outputs["calculate"] == 20


def test_execution_order():
    workflow = Workflow()
    execution = []

    workflow.add_task(Task(
        name="first",
        function=lambda inputs, params: execution.append("first")
    ))

    workflow.add_task(Task(
        name="second",
        function=lambda inputs, params: execution.append("second"),
        dependencies=frozenset({"first"})
    ))

    run(workflow)

    assert execution == ["first", "second"]


def test_task_failure():
    workflow = Workflow()

    def failing_task(inputs, params):
        raise ValueError("Test error")

    workflow.add_task(Task(
        name="failure",
        function=failing_task
    ))

    with pytest.raises(TaskExecutionError) as error:
        run(workflow)

    assert error.value.task_name == "failure"
    assert isinstance(error.value.__cause__, ValueError)
    assert error.value.result.task_states["failure"].status == TaskStatus.FAILED


def test_dependent_task_skipped():
    workflow = Workflow()

    workflow.add_task(Task(
        name="failure",
        function=lambda inputs, params: 1 / 0
    ))

    workflow.add_task(Task(
        name="dependent",
        function=lambda inputs, params: 100,
        dependencies=frozenset({"failure"})
    ))

    with pytest.raises(TaskExecutionError) as error:
        run(workflow)

    states = error.value.result.task_states

    assert states["failure"].status == TaskStatus.FAILED
    assert states["dependent"].status == TaskStatus.SKIPPED


def test_independent_task_continues():
    workflow = Workflow()

    workflow.add_task(Task(
        name="failure",
        function=lambda inputs, params: 1 / 0
    ))

    workflow.add_task(Task(
        name="independent",
        function=lambda inputs, params: "OK"
    ))

    with pytest.raises(TaskExecutionError) as error:
        run(workflow)

    states = error.value.result.task_states

    assert states["failure"].status == TaskStatus.FAILED
    assert states["independent"].status == TaskStatus.SUCCEEDED


def test_execution_time():
    workflow = Workflow()

    workflow.add_task(Task(
        name="task",
        function=lambda inputs, params: 123
    ))

    result = run(workflow)

    assert result.duration >= 0
    assert result.task_states["task"].duration >= 0
