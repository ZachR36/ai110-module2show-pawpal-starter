# PawPal+

PawPal+ is a class project from my CodePath AI110 course, built with Claude Code. It is a Python and Streamlit application that helps pet owners organize care tasks and create a daily plan based on their available time and scheduling preferences.

The project explores object-oriented design, greedy scheduling, automated testing, and connecting a Python backend to an interactive web interface.

## Features

- **Multiple pets:** Manage pets and their individual care tasks in one place.
- **Task management:** Add and remove tasks with a duration, priority, and optional fixed start time; mark tasks complete and view completion history.
- **Recurring care:** Completing a daily or weekly task creates its next occurrence with an updated due date.
- **Configurable scheduling:** Choose priority order, shortest tasks first, or grouping by pet.
- **Two plan formats:** Generate a simple task list or a schedule with start and end times, with support for custom availability windows.
- **Schedule explanations:** See the selection rationale, tasks skipped because of the time budget, remaining time, and warnings about fixed-time placement or overlapping tasks.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead. Open the local URL printed by Streamlit.

To run the command-line walkthrough:

```bash
python main.py
```

The application uses rule-based scheduling and does not require an AI API key.

## Walkthrough

1. **Configure your profile.** Open **Configure Owner & Preferences**, enter your name, set a daily time budget and start hour, and choose a sorting preference. Optionally add custom availability windows.
2. **Add pets.** Open **Add Pet** and enter a name and species for each pet.
3. **Create care tasks.** Under **Add New Task**, select a pet, enter a description and duration, choose a priority and recurrence, and optionally specify a time in 24-hour `HH:MM` format.
4. **Generate a plan.** Choose **Simple (task list)** or **With Times (slots)** and click **Generate Schedule**. Simple plans can be grouped by pet or completion status. Review the **Plan** and **Details** tabs for the schedule, explanations, and metrics.
5. **Track progress.** Expand a pet's task list to mark tasks complete, remove tasks, and review completed care. Generate a new plan after making changes.

### Example plan

The CLI demo includes an owner with 120 minutes available and two pets. Its priority-based simple plan includes:

```text
Daily plan for Jordan:

Biscuit:
  - Morning walk (30 min) [priority: high]
  - Playtime (20 min) [priority: medium]
  - Treat (5 min) [priority: low]

Whiskers:
  - Feeding (5 min) [priority: high]
  - Litter box cleaning (10 min) [priority: medium]
  - Grooming (15 min) [priority: low]

Total time scheduled: 85 min / 120 min available
Time remaining: 35 min
```

Tasks are selected in the chosen sort order, then grouped for display. The application also explains the selection and lists any tasks skipped because they exceed the remaining budget.

## Design and scheduling

The Streamlit interface is separate from the domain model and scheduling logic, so the backend can also run through the CLI and unit tests.

| Component | Responsibility |
| --- | --- |
| `Task` | Care activity, duration, priority, recurrence, due date, and completion state |
| `Pet` | Pet information, active tasks, and completed task history |
| `Owner` | Pets, daily time budget, sorting preference, and availability windows |
| `TimeWindow` | Start and end times for an availability interval |
| `Scheduler` | Task selection, grouping, time placement, conflict detection, and explanations |

### Task selection

The scheduler sorts active tasks and greedily selects each task that fits the remaining time budget.

| Strategy | Ordering |
| --- | --- |
| Priority | High → medium → low, with shorter tasks first within each priority |
| Duration | Shortest → longest |
| Pet | Pet ID order, then priority within each pet |

This approach keeps selection predictable and easy to explain. It does not optimize for every possible combination of tasks or guarantee the best use of available time.

### Time placement and recurrence

Timed scheduling first selects tasks against the daily budget, then attempts to place fixed-time tasks before filling remaining slots. Fixed-time tasks that conflict or fall outside availability windows produce warnings and are reconsidered as flexible tasks. A final conflict check reports overlaps.

Completing a recurring task moves it into completion history and adds a new active instance, advancing its due date by one day or one week.

## Tests

```bash
python -m pytest tests/test_pawpal.py -v
```

The test suite covers task and pet management, daily and weekly recurrence, all three sorting strategies, time-budget selection, fixed-time scheduling, availability windows, conflict detection, grouping, and time conversion helpers. It also includes cases with no pets or no available time.

## Project structure

```text
app.py                 Streamlit interface and session state
pawpal_system.py       Domain classes and scheduling logic
main.py                Command-line demonstrations
requirements.txt       Streamlit and pytest dependencies
tests/test_pawpal.py   Backend unit tests
diagrams/              Mermaid UML diagrams
```

## Current limitations

- Data is stored in Streamlit session state; there is no database or persistent storage.
- Recurring tasks receive future due dates, but task selection does not yet filter by due date.
- Timed placement can span gaps between available slots, so overlaps or window-boundary issues remain possible. Conflict warnings help surface overlaps; stricter contiguous-slot validation is a next step.

These are the main areas for further development, alongside splitting the scheduler into smaller components as its responsibilities grow.
