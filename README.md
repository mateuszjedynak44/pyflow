# PyFlow

PyFlow to biblioteka napisana w języku Python, służąca do definiowania, walidowania, planowania i wykonywania przepływów danych (workflow).

Projekt umożliwia tworzenie zadań, określanie zależności między nimi, sprawdzanie poprawności grafu skierowanego acyklicznego (DAG), planowanie kolejności wykonywania oraz synchroniczne uruchamianie całego przepływu.

## Wymagania

- Python 3.11 lub nowszy
- Git
- pytest

## Struktura projektu

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

## Instalacja

Sklonuj repozytorium i przejdź do katalogu projektu.

Utwórz środowisko wirtualne:

```bash
python -m venv .venv
```

Aktywuj środowisko w systemie Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Zainstaluj pakiet:

```bash
python -m pip install -e ".[dev]"
```

## Funkcjonalności

- Model zadania oparty na dataclasses.
- Model przepływu Workflow do zarządzania zadaniami.
- Definiowanie zależności między zadaniami.
- Walidacja grafu DAG.
- Wykrywanie brakujących zależności i cykli.
- Deterministyczne sortowanie topologiczne.
- Wyznaczanie warstw wykonania.
- Synchroniczny silnik wykonawczy.
- Przekazywanie wyników pomiędzy zależnymi zadaniami.
- Monitorowanie statusów wykonywanych zadań.
- Obsługa błędów i pomijanie zadań zależnych.
- Pomiar czasu wykonania.
- Generowanie raportu z przebiegu workflow.
- Automatyczne testy jednostkowe i integracyjne.

## Modele Task i Workflow

Każde zadanie (Task) zawiera następujące elementy:

- name - unikalna nazwa zadania.
- function - funkcja wykonywana przez silnik.
- dependencies - zbiór bezpośrednich zależności.
- params - parametry konfiguracyjne zadania.
- description - opcjonalny opis zadania.

Funkcje zadań korzystają z następującego interfejsu:

```python
def task_function(inputs, params):
    return result
```

Argument inputs zawiera wyniki bezpośrednich zależności, natomiast params przechowuje parametry konfiguracyjne zadania.

Klasa Workflow przechowuje zadania i odpowiada za walidację definicji przepływu.

## Planowanie grafu

Projekt wykorzystuje algorytm sortowania topologicznego Kahna.

Algorytm wyznacza poprawną kolejność wykonywania zadań, zapewniając, że każde zadanie zostanie uruchomione dopiero po wykonaniu wszystkich swoich zależności.

W przypadku kilku dostępnych zadań stosowana jest kolejność alfabetyczna, co zapewnia deterministyczność wyników.

Złożoność czasowa zastosowanego wariantu z kopcem wynosi:

O((V + E) log V)

Gdzie:
- V oznacza liczbę zadań.
- E oznacza liczbę zależności.

Warstwy wykonania grupują zadania, których zależności zostały już spełnione.

## Synchroniczny silnik wykonawczy

Silnik wykonawczy znajduje się w pliku execution.py.

Główną funkcją odpowiedzialną za uruchamianie przepływu jest:

```python
from pyflow import run

result = run(workflow)
```

Obiekt RunResult przechowuje:

- outputs - mapowanie nazw zadań na uzyskane wyniki.
- task_states - status i informacje o wykonaniu każdego zadania.
- succeeded - informację, czy cały przepływ zakończył się powodzeniem.
- duration - całkowity czas wykonania workflow.

## Statusy zadań

Każde zadanie może posiadać jeden z następujących statusów:

| Status | Opis |
|--------|------|
| PENDING | Zadanie oczekuje na wykonanie. |
| RUNNING | Zadanie jest aktualnie wykonywane. |
| SUCCEEDED | Zadanie zakończyło się powodzeniem. |
| FAILED | Wykonanie zadania zakończyło się błędem. |
| SKIPPED | Zadanie zostało pominięte z powodu błędu zależności. |

## Polityka obsługi błędów

PyFlow wykorzystuje politykę, która pozwala na kontynuowanie wykonywania niezależnych zadań pomimo wystąpienia błędu.

W przypadku niepowodzenia zadania:

1. Zadanie otrzymuje status FAILED.
2. Zadania zależne otrzymują status SKIPPED.
3. Zadania niezależne są nadal wykonywane.
4. Po przetworzeniu przepływu silnik zgłasza wyjątek TaskExecutionError.

TaskExecutionError zawiera nazwę zadania, w którym wystąpił błąd, oryginalny wyjątek oraz raport wykonania.

Oryginalny wyjątek jest zachowywany poprzez mechanizm łańcuchowania wyjątków.

## Raport czasu wykonania

Silnik mierzy czas wykonania przy użyciu funkcji time.perf_counter().

Raport zawiera:

- Nazwę każdego zadania.
- Status wykonania zadania.
- Indywidualny czas wykonania.
- Całkowity czas wykonania workflow.
- Informację o powodzeniu lub niepowodzeniu całego przepływu.

## Przykładowy workflow

Projekt zawiera kompletny przykład przepływu danych:

CSV -> Czyszczenie danych -> Agregacja -> JSON

Przykład odczytuje lokalny plik CSV, weryfikuje rekordy, oblicza statystyki i generuje raport w formacie JSON.

Uruchomienie przykładu:

```bash
python examples/run_example.py
```

Wygenerowany raport zostanie zapisany w pliku:

```text
examples/report.json
```

## Uruchamianie testów

Aby uruchomić wszystkie testy automatyczne, wykonaj polecenie:

```bash
python -m pytest -v
```

Testy obejmują:

- Puste przepływy.
- Pojedyncze zadania.
- Zależności pomiędzy zadaniami.
- Duplikaty zadań.
- Brakujące zależności.
- Wykrywanie cykli.
- Deterministyczność kolejności wykonania.
- Warstwy wykonania.
- Przekazywanie wyników.
- Parametry zadań.
- Obsługę błędów wykonania.
- Pomijanie zadań zależnych.
- Kontynuowanie wykonywania zadań niezależnych.
- Pomiar czasu wykonania.

## Publiczne API

Główne elementy biblioteki są dostępne bezpośrednio z pakietu pyflow:

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

## Rozwój projektu

Projekt został opracowany z wykorzystaniem języka Python w wersji 3.11 lub nowszej.

Implementacja została podzielona na trzy główne obszary:

- Models - definicje zadań i przepływów.
- Graph - walidacja grafu DAG i planowanie kolejności wykonania.
- Execution - synchroniczne wykonywanie przepływów, obsługa błędów i raportowanie.

Wszystkie najważniejsze funkcjonalności zostały objęte testami automatycznymi.
