
import pytest

from pyflow import (
    Task,
    Workflow,
    WorkflowValidationError,
    execution_layers,
    topological_order,
)


def dummy_function(inputs, params):
    return None


def test_empty_workflow():
    workflow = Workflow()

    assert topological_order(workflow) == []
    assert execution_layers(workflow) == []


def test_single_task():
    workflow = Workflow()
    workflow.add_task(Task("extract", dummy_function))

    assert topological_order(workflow) == ["extract"]
    assert execution_layers(workflow) == [["extract"]]


def test_task_chain():
    workflow = Workflow()
    workflow.add_task(Task("a", dummy_function))
    workflow.add_task(
        Task("b", dummy_function, frozenset({"a"}))
    )
    workflow.add_task(
        Task("c", dummy_function, frozenset({"b"}))
    )

    assert topological_order(workflow) == ["a", "b", "c"]
    assert execution_layers(workflow) == [["a"], ["b"], ["c"]]


def test_independent_tasks_are_sorted():
    workflow = Workflow()

    workflow.add_task(Task("z", dummy_function))
    workflow.add_task(Task("a", dummy_function))
    workflow.add_task(Task("m", dummy_function))

    assert topological_order(workflow) == ["a", "m", "z"]
    assert execution_layers(workflow) == [["a", "m", "z"]]


def test_branching_workflow_layers():
    workflow = Workflow()
    workflow.add_task(Task("extract", dummy_function))
    workflow.add_task(
        Task("clean_a", dummy_function, frozenset({"extract"}))
    )
    workflow.add_task(
        Task("clean_b", dummy_function, frozenset({"extract"}))
    )
    workflow.add_task(
        Task(
            "report",
            dummy_function,
            frozenset({"clean_a", "clean_b"}),
        )
    )

    assert execution_layers(workflow) == [
        ["extract"],
        ["clean_a", "clean_b"],
        ["report"],
    ]


def test_cycle_is_rejected():
    workflow = Workflow()
    workflow.add_task(
        Task("a", dummy_function, frozenset({"b"}))
    )
    workflow.add_task(
        Task("b", dummy_function, frozenset({"a"}))
    )

    with pytest.raises(WorkflowValidationError, match="cycle"):
        workflow.validate()


def test_topological_order_is_deterministic():
    workflow = Workflow()
    workflow.add_task(Task("z", dummy_function))
    workflow.add_task(Task("a", dummy_function))
    workflow.add_task(
        Task("b", dummy_function, frozenset({"a"}))
    )

    first = topological_order(workflow)

    for _ in range(10):
        assert topological_order(workflow) == first


def test_every_task_appears_once():
    workflow = Workflow()
    workflow.add_task(Task("a", dummy_function))
    workflow.add_task(
        Task("b", dummy_function, frozenset({"a"}))
    )
    workflow.add_task(
        Task("c", dummy_function, frozenset({"a"}))
    )

    order = topological_order(workflow)

    assert len(order) == len(set(order)) == 3
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")


def test_unknown_dependency_in_graph_function():
    workflow = Workflow()
    workflow.add_task(
        Task("b", dummy_function, frozenset({"missing"}))
    )

    with pytest.raises(WorkflowValidationError, match="unknown dependency"):
        topological_order(workflow)
