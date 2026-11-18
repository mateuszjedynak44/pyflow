import csv
import json
from pathlib import Path

from pyflow.models import Task, Workflow
from pyflow.execution import run, TaskExecutionError, TaskStatus


BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "sales.csv"
JSON_FILE = BASE_DIR / "report.json"


def read_csv(inputs, params):
    with open(params["path"], "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def clean_records(inputs, params):
    records = inputs["read_csv"]
    cleaned = []

    for record in records:
        quantity = int(record["quantity"])
        price = float(record["price"])

        if quantity > 0 and price >= 0:
            cleaned.append({
                "product": record["product"],
                "quantity": quantity,
                "price": price
            })

    return cleaned


def aggregate(inputs, params):
    records = inputs["clean_records"]

    total_quantity = sum(record["quantity"] for record in records)
    total_value = sum(
        record["quantity"] * record["price"]
        for record in records
    )

    return {
        "products_count": len(records),
        "total_quantity": total_quantity,
        "total_value": round(total_value, 2)
    }


def generate_json(inputs, params):
    report = inputs["aggregate"]

    with open(params["path"], "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report


def print_report(result):
    print("\n========== WORKFLOW REPORT ==========")

    for name, state in result.task_states.items():
        print(
            f"{name}: {state.status.value} | "
            f"time: {state.duration:.6f} s"
        )

    print("-------------------------------------")
    print(f"Total execution time: {result.duration:.6f} s")
    print(f"Workflow succeeded: {result.succeeded}")
    print("=====================================")


def main():
    workflow = Workflow()

    workflow.add_task(Task(
        name="read_csv",
        function=read_csv,
        params={"path": str(CSV_FILE)}
    ))

    workflow.add_task(Task(
        name="clean_records",
        function=clean_records,
        dependencies=frozenset({"read_csv"})
    ))

    workflow.add_task(Task(
        name="aggregate",
        function=aggregate,
        dependencies=frozenset({"clean_records"})
    ))

    workflow.add_task(Task(
        name="generate_json",
        function=generate_json,
        dependencies=frozenset({"aggregate"}),
        params={"path": str(JSON_FILE)}
    ))

    try:
        result = run(workflow)
        print_report(result)
        print(f"\nJSON report saved to: {JSON_FILE}")

    except TaskExecutionError as error:
        print(f"Execution failed: {error}")
        print_report(error.result)


if __name__ == "__main__":
    main()
