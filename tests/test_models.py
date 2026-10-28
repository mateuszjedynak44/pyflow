
import pytest

from pyflow import Task, Workflow, WorkflowValidationError


def dummy_function(inputs, params):
    return None


def test_task_creation():
    task = Task("extract", dummy_function)

    assert task.name == "extract"
    assert task.dependencies == frozenset()
    assert task.params == {}


def test_empty_task_name_is_rejected():
    with pytest.raises(ValueError):
        Task("", dummy_function)


def test_task_cannot_depend_on_itself():
    with pytest.raises(ValueError):
        Task(
            "extract",
            dummy_function,
            dependencies=frozenset({"extract"}),
        )


def test_task_parameters_are_copied():
    params = {"limit": 10}
    task = Task("extract", dummy_function, params=params)

    params["limit"] = 100

    assert task.params["limit"] == 10


def test_task_parameters_cannot_be_reassigned():
    task = Task("extract", dummy_function, params={"limit": 10})

    with pytest.raises(TypeError):
        task.params["limit"] = 100


def test_workflow_adds_task():
    workflow = Workflow()
    task = Task("extract", dummy_function)

    workflow.add_task(task)

    assert workflow.tasks["extract"] is task


def test_duplicate_task_is_rejected():
    workflow = Workflow()
    workflow.add_task(Task("extract", dummy_function))

    with pytest.raises(ValueError, match="already registered"):
        workflow.add_task(Task("extract", dummy_function))


def test_missing_dependency_is_rejected():
    workflow = Workflow()
    workflow.add_task(
        Task(
            "clean",
            dummy_function,
            dependencies=frozenset({"extract"}),
        )
    )

    with pytest.raises(
        WorkflowValidationError,
        match="unknown dependencies",
    ):
        workflow.validate()


def test_workflow_rejects_non_task():
    workflow = Workflow()

    with pytest.raises(TypeError):
        workflow.add_task("extract")
