# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

(Note - my program doesn't fit the schedule into specific hours of the day like the example left by the teachers here. Mine tells the user which tasks they have time for today and in which order to do them based on priority, and grouped by pets. The instructions never required
this feature, and since I didn't ask Claude for it my initial model was not built that way.)

```
Daily plan for Jordan:

Biscuit:
  - Feeding (10 min) [priority: high]
  - Morning walk (30 min) [priority: high]
  - Playtime (20 min) [priority: medium]

Whiskers:
  - Feeding (5 min) [priority: high]
  - Litter box cleaning (10 min) [priority: medium]

Total time scheduled: 75 min

Time remaining: 45 minutes
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ implements a multi-faceted scheduling system that handles task prioritization, filtering, time-slot allocation, conflict detection, and recurring task management.

### Sorting Behavior

The scheduler supports three configurable sort strategies (set via `Owner.sort_preference`):

| Strategy | Method | Behavior |
|----------|--------|----------|
| **Priority** (default) | `Scheduler.sort_by_priority()` | Tasks ordered by importance: high → medium → low, then by duration. High-priority tasks are scheduled first. |
| **Duration** | `Scheduler.sort_by_duration()` | Tasks ordered shortest to longest. Maximizes task count by fitting smaller tasks first. |
| **Pet** | `Scheduler.sort_by_pet()` | Tasks grouped by pet, completing all tasks for one pet before moving to the next. Maintains priority within each pet. |

The `Scheduler.get_sorted_tasks()` method dispatches to the appropriate sorting strategy based on the owner's preference.

### Filtering Behavior

After tasks are selected for the day, they can be organized in two ways (set via `filter_by` parameter in `Scheduler.filter_schedule()`):

| Filter | Method | Result |
|--------|--------|--------|
| **By Pet** (default) | `Scheduler.filter_schedule(..., filter_by="pet")` | Schedule grouped by pet name. Shows all tasks for each pet together. |
| **By Completion** | `Scheduler.filter_schedule(..., filter_by="completion")` | Schedule split into "completed" and "pending" tasks. Useful for progress tracking. |

The `Scheduler.build_schedule()` method combines task selection and filtering into one call.

### Time-Slot Allocation

Tasks are scheduled into specific time slots using `Scheduler.schedule_with_times()`, which implements a two-phase algorithm:

**Phase 1: Fixed-time tasks** (`schedule_with_times()` main loop)
- User-pinned tasks (with `Task.scheduled_time` set) are placed first, in priority order
- Each fixed task is validated:
  - `Scheduler._time_in_window()` — Ensure start time is within availability windows
  - `Scheduler._can_fit_in_window()` — Ensure task duration fits without crossing window boundaries
  - Collision detection — Check for conflicts with already-placed fixed tasks
- If a fixed task fails validation or conflicts, it's rejected and added to the floating pool

**Phase 2: Floating tasks** (`Scheduler._place_floating_tasks()`)
- Remaining floating tasks are sorted by owner preference
- `Scheduler.find_available_slots()` computes free 1-minute slots across all availability windows
- Tasks are greedily placed into consecutive available slots in sort order

**Helper utilities:**
- `Scheduler._time_to_minutes(time_str)` — Convert "HH:MM" to minutes since midnight
- `Scheduler._minutes_to_time(total_minutes)` — Convert minutes back to "HH:MM" format

### Availability Windows

The owner can define multiple time windows when they're available:

- Default: Single window from `start_hour` to `start_hour + available_time` (backward compatible)
- Custom: `Owner.set_availability_windows([TimeWindow(...), TimeWindow(...)])` for non-contiguous schedules
- Example: 8am-12pm, 2pm-6pm (splits for lunch)

### Conflict Detection

`Scheduler.detect_conflicts()` scans the final schedule to identify overlapping tasks:
- Compares all task pairs for time overlap
- Returns human-readable warnings like: `"'Dog walk' (09:00-09:30) overlaps with 'Cat feeding' (09:15-09:20)"`
- Works for same-pet and cross-pet conflicts
- Does not modify the schedule—purely diagnostic

Note: Our scheduling algorithm *prevents* conflicts by design (fixed tasks win collisions, floating tasks only fill available slots). Conflict detection is provided for validation and edge cases.

### Recurring Task Logic

Tasks can be set to recur daily or weekly via `Task.recurrence_type`:

**Task completion flow:**
1. Owner calls `Pet.complete_task(task_id)`
2. Task is marked complete via `Task.mark_complete()` (sets `completed=True` and `completed_on=datetime.now()`)
3. Task is moved to `Pet.completed_tasks` (archived)
4. If task is recurring (`recurrence_type` is "daily" or "weekly"):
   - `Task.create_next_occurrence()` clones the task with:
     - New ID (original_id + 1000) to avoid collisions
     - New `due_date` calculated using `timedelta`:
       - Daily: `due_date + timedelta(days=1)`
       - Weekly: `due_date + timedelta(weeks=1)`
   - New task is added to `Pet.tasks` for the next scheduling cycle

**Example:**
```python
# Create a daily recurring task
task = Task(id=1, description="Feed dog", recurrence_type="daily", 
            due_date=datetime(2026, 7, 6))
pet.add_task(task)

# Owner marks it complete
pet.complete_task(1)

# Automatically creates next occurrence:
# New task: id=1001, due_date=2026-07-07, same description/duration/priority
```

Non-recurring tasks (`recurrence_type="once"`) are simply archived when completed.

### Task Selection Algorithm

`Scheduler.select_tasks_for_day()` implements greedy task selection:
1. Fetch all active tasks via `Scheduler.get_tasks()` (completed tasks are excluded)
2. Sort by owner preference via `Scheduler.get_sorted_tasks()`
3. Iterate through sorted tasks, adding each if it fits in `available_minutes`
4. Reject remaining tasks as skipped (with reasoning provided in explanations)

**Rationale:** Greedy respects sort priority (e.g., users expect high-priority tasks to be scheduled first, not demoted for better bin-packing). Simple, predictable, and transparent to users.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
