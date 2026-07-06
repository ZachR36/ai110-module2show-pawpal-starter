from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class TimeWindow:
    start_time: str
    end_time: str
    day_of_week: str = "daily"

    def contains_time(self, hour: int, minute: int) -> bool:
        """Check if a time (hour:minute) falls within this window."""
        start_h, start_m = map(int, self.start_time.split(":"))
        end_h, end_m = map(int, self.end_time.split(":"))
        time_minutes = hour * 60 + minute
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        return start_minutes <= time_minutes < end_minutes


@dataclass
class Task:
    id: int
    description: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False
    scheduled_time: str | None = None
    completed_on: datetime | None = None
    recurrence_type: str = "once"
    due_date: datetime | None = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True
        self.completed_on = datetime.now()

    def is_overdue(self, current_time: datetime) -> bool:
        """Check if this task is overdue based on the current time."""
        if self.completed:
            return False
        return current_time.hour > 20

    def set_scheduled_time(self, time: str) -> None:
        """Set a specific time for this task (HH:MM format)."""
        self.scheduled_time = time

    def clear_scheduled_time(self) -> None:
        """Clear the scheduled time for this task."""
        self.scheduled_time = None

    def set_due_date(self, due_date: datetime) -> None:
        """Set the due date for this task."""
        self.due_date = due_date

    def create_next_occurrence(self) -> "Task":
        """Create a new instance of this task for the next occurrence (daily or weekly)."""
        if self.recurrence_type == "once":
            return None

        new_task = Task(
            id=self.id + 1000,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            scheduled_time=self.scheduled_time,
            completed_on=None,
            recurrence_type=self.recurrence_type,
            due_date=None
        )

        if self.recurrence_type == "daily":
            new_task.due_date = self.due_date + timedelta(days=1) if self.due_date else datetime.now() + timedelta(days=1)
        elif self.recurrence_type == "weekly":
            new_task.due_date = self.due_date + timedelta(weeks=1) if self.due_date else datetime.now() + timedelta(weeks=1)

        return new_task


@dataclass
class Pet:
    id: int
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)
    completed_tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet's task list by ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def complete_task(self, task_id: int) -> bool:
        """Mark a task complete and move it to completed_tasks. Auto-create next occurrence for recurring tasks."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return False
        task.mark_complete()
        self.tasks.remove(task)

        if task.recurrence_type == "once":
            self.completed_tasks.append(task)
        else:
            # Create next occurrence for daily/weekly tasks
            next_task = task.create_next_occurrence()
            if next_task:
                self.add_task(next_task)
            self.completed_tasks.append(task)

        return True

    def get_tasks(self) -> list[Task]:
        """Return all active (non-completed) tasks for this pet."""
        return self.tasks


class Owner:
    def __init__(self, name: str, available_time: int, start_hour: int = 8, sort_preference: str = "priority", preferences: dict = None):
        self.name = name
        self.available_time = available_time
        self.start_hour = start_hour
        self.sort_preference = sort_preference
        self.preferences = preferences if preferences else {}
        self.pets = []
        self.availability_windows = self._create_default_window()

    def _create_default_window(self) -> list[TimeWindow]:
        """Create a default availability window from start_hour and available_time.

        Initializes a single contiguous time window based on the owner's start time
        and total available minutes per day. Used for backward compatibility when
        no explicit availability windows are set.
        """
        end_hour = self.start_hour + (self.available_time // 60)
        end_minute = self.available_time % 60
        start_time = f"{self.start_hour:02d}:00"
        end_time = f"{end_hour:02d}:{end_minute:02d}"
        return [TimeWindow(start_time=start_time, end_time=end_time)]

    def set_availability_windows(self, windows: list[TimeWindow]) -> None:
        """Set custom availability windows for the owner.

        Allows the owner to define specific time slots when they are available
        to do pet care tasks (e.g., 8am-12pm, 2pm-6pm). The scheduler will only
        place tasks within these windows.

        Args:
            windows: List of TimeWindow objects defining available time slots.
        """
        self.availability_windows = windows

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet from this owner's pet list by ID."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_tasks(self) -> list[Task]:
        """Retrieve all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high → low) and duration."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (priority_order.get(t.priority, 3), t.duration_minutes))

    def sort_by_duration(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by duration (shortest first)."""
        return sorted(tasks, key=lambda t: t.duration_minutes)

    def sort_by_pet(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by pet, completing all tasks for one pet before moving to the next."""
        # Build a map of task to pet
        task_to_pet = {}
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                task_to_pet[task.id] = pet.id

        # Sort by pet id, then by priority within each pet
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda t: (task_to_pet.get(t.id, float('inf')), priority_order.get(t.priority, 3))
        )

    def get_sorted_tasks(self, tasks: list[Task]) -> list[Task]:
        """Apply the owner's preferred sorting method."""
        if self.owner.sort_preference == "duration":
            return self.sort_by_duration(tasks)
        elif self.owner.sort_preference == "pet":
            return self.sort_by_pet(tasks)
        else:  # default to "priority"
            return self.sort_by_priority(tasks)

    def _time_to_minutes(self, time_str: str) -> int:
        """Convert "HH:MM" to total minutes since midnight.

        Args:
            time_str: Time string in "HH:MM" format.

        Returns:
            Total minutes since midnight (0-1439).
        """
        hour, minute = map(int, time_str.split(":"))
        return hour * 60 + minute

    def _minutes_to_time(self, total_minutes: int) -> str:
        """Convert total minutes since midnight to "HH:MM" format.

        Args:
            total_minutes: Total minutes since midnight.

        Returns:
            Time string in "HH:MM" format with zero-padding.
        """
        hour = total_minutes // 60
        minute = total_minutes % 60
        return f"{hour:02d}:{minute:02d}"

    def partition_tasks(self, tasks: list[Task]) -> dict:
        """Separate tasks into fixed-time and floating.

        Partitions a list of tasks into two groups: those with a scheduled_time
        (fixed-time tasks that must run at a specific time) and those without
        (floating tasks that can be scheduled into any available slot).

        Args:
            tasks: List of Task objects to partition.

        Returns:
            Dictionary with keys 'fixed' and 'floating', each containing a list of tasks.
        """
        fixed = [t for t in tasks if t.scheduled_time]
        floating = [t for t in tasks if not t.scheduled_time]
        return {"fixed": fixed, "floating": floating}

    def _time_in_window(self, hour: int, minute: int) -> bool:
        """Check if a time falls within any availability window.

        Validates whether a specific time (hour:minute) falls within at least one
        of the owner's availability windows.

        Args:
            hour: Hour component (0-23).
            minute: Minute component (0-59).

        Returns:
            True if the time is within at least one availability window, False otherwise.
        """
        for window in self.owner.availability_windows:
            if window.contains_time(hour, minute):
                return True
        return False

    def _can_fit_in_window(self, start_hour: int, start_minute: int, duration: int) -> bool:
        """Check if a task can fit entirely within availability windows.

        Validates that a task of given duration starting at a specific time can
        complete without leaving any availability window. Returns False if the
        task would span outside a window or cross a gap.

        Args:
            start_hour: Starting hour (0-23).
            start_minute: Starting minute (0-59).
            duration: Task duration in minutes.

        Returns:
            True if the entire task fits within availability windows, False otherwise.
        """
        current_hour, current_minute = start_hour, start_minute
        remaining_duration = duration

        while remaining_duration > 0:
            if not self._time_in_window(current_hour, current_minute):
                return False
            current_minute += 1
            if current_minute >= 60:
                current_minute = 0
                current_hour += 1
            remaining_duration -= 1

        return True

    def detect_conflicts(self, timed_tasks: list[dict]) -> list[str]:
        """Detect and report scheduling conflicts between tasks.

        Scans a finalized schedule to identify any two tasks that overlap in time.
        Conflicts can occur between tasks for the same pet or different pets.
        Returns human-readable warning messages without modifying the schedule.

        Args:
            timed_tasks: List of scheduled task dictionaries, each containing
                'task', 'start_time', and 'end_time' keys.

        Returns:
            List of conflict warning messages. Empty list if no conflicts detected.
        """
        warnings = []
        task_to_pet = {}

        # Build a map of task ID to pet name
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                task_to_pet[task.id] = pet.name
            # Also check completed tasks
            for task in pet.completed_tasks:
                task_to_pet[task.id] = pet.name

        # Check each pair of tasks for time overlap
        for i in range(len(timed_tasks)):
            for j in range(i + 1, len(timed_tasks)):
                task_i = timed_tasks[i]["task"]
                task_j = timed_tasks[j]["task"]
                start_i, end_i = timed_tasks[i]["start_time"], timed_tasks[i]["end_time"]
                start_j, end_j = timed_tasks[j]["start_time"], timed_tasks[j]["end_time"]

                # Convert times to minutes for comparison
                start_i_min = int(start_i.split(":")[0]) * 60 + int(start_i.split(":")[1])
                end_i_min = int(end_i.split(":")[0]) * 60 + int(end_i.split(":")[1])
                start_j_min = int(start_j.split(":")[0]) * 60 + int(start_j.split(":")[1])
                end_j_min = int(end_j.split(":")[0]) * 60 + int(end_j.split(":")[1])

                # Check for overlap: if one doesn't end before the other starts, they overlap
                if not (end_i_min <= start_j_min or end_j_min <= start_i_min):
                    pet_i = task_to_pet.get(task_i.id, "Unknown")
                    pet_j = task_to_pet.get(task_j.id, "Unknown")
                    warnings.append(
                        f"Conflict: '{task_i.description}' ({start_i}-{end_i}) for {pet_i} "
                        f"overlaps with '{task_j.description}' ({start_j}-{end_j}) for {pet_j}"
                    )

        return warnings

    def find_available_slots(self, occupied_times: list[tuple]) -> list[tuple]:
        """Find available time slots after placing fixed tasks.

        Computes free 1-minute slots within all availability windows, excluding
        any time already occupied by fixed-time tasks. Returns a list of available
        (hour, minute) tuples for floating tasks to be scheduled into.

        Args:
            occupied_times: List of (start_minute, end_minute) tuples representing
                times already occupied by fixed tasks.

        Returns:
            List of (hour, minute) tuples representing available time slots.
        """
        slots = []
        for window in self.owner.availability_windows:
            start_h, start_m = map(int, window.start_time.split(":"))
            end_h, end_m = map(int, window.end_time.split(":"))

            current_h, current_m = start_h, start_m
            end_minutes = end_h * 60 + end_m

            while current_h * 60 + current_m < end_minutes:
                slot_start = (current_h, current_m)
                is_occupied = any(
                    start <= current_h * 60 + current_m < end
                    for start, end in occupied_times
                )

                if not is_occupied:
                    slots.append((current_h, current_m))

                current_m += 1
                if current_m >= 60:
                    current_m = 0
                    current_h += 1

        return slots

    def select_tasks_for_day(self, available_minutes: int) -> dict:
        """Select which tasks fit into available time based on priority/sorting.

        Applies the owner's preferred sorting method (priority, duration, or pet)
        to all tasks, then greedily selects tasks that fit within available time
        until time runs out. Returns both scheduled and skipped tasks.

        Args:
            available_minutes: Total minutes available for the day.

        Returns:
            Dictionary with keys 'scheduled_tasks', 'skipped_tasks', and 'time_remaining'.
        """
        tasks = self.get_tasks()
        prioritized = self.get_sorted_tasks(tasks)

        time_remaining = available_minutes
        scheduled_tasks = []
        skipped_tasks = []

        for task in prioritized:
            if time_remaining >= task.duration_minutes:
                scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes
            else:
                skipped_tasks.append(task)

        return {
            "scheduled_tasks": scheduled_tasks,
            "skipped_tasks": skipped_tasks,
            "time_remaining": time_remaining
        }

    def filter_schedule(self, scheduled_tasks: list[Task], filter_by: str = "pet") -> dict:
        """Filter/group scheduled tasks by pet (default) or by completion status.

        Takes a list of scheduled tasks and organizes them for display either
        by pet (default) or by completion status (completed/pending).

        Args:
            scheduled_tasks: List of Task objects to filter.
            filter_by: Filter method - "pet" (default) or "completion".

        Returns:
            Dictionary of tasks organized by the chosen filter method.
        """
        if filter_by == "completion":
            completed = [t for t in scheduled_tasks if t.completed]
            pending = [t for t in scheduled_tasks if not t.completed]
            return {
                "completed": completed,
                "pending": pending
            }
        else:  # default to "pet"
            schedule_by_pet = {}
            for pet in self.owner.pets:
                pet_tasks = [t for t in scheduled_tasks if t in pet.get_tasks()]
                if pet_tasks:
                    schedule_by_pet[pet.name] = pet_tasks
            return schedule_by_pet

    def build_schedule(self, available_minutes: int, filter_by: str = "pet") -> dict:
        """Build a daily schedule: select tasks that fit, then filter/group them.

        Orchestrates the full scheduling workflow: selects tasks that fit in
        available time (respecting sort preference), then organizes them by
        the chosen filter method (pet or completion status).

        Args:
            available_minutes: Total minutes available for the day.
            filter_by: How to group results - "pet" (default) or "completion".

        Returns:
            Dictionary with 'schedule', 'scheduled_tasks', 'skipped_tasks', and 'time_remaining'.
        """
        selection = self.select_tasks_for_day(available_minutes)
        scheduled_tasks = selection["scheduled_tasks"]
        filtered = self.filter_schedule(scheduled_tasks, filter_by)

        return {
            "schedule": filtered,
            "scheduled_tasks": scheduled_tasks,
            "skipped_tasks": selection["skipped_tasks"],
            "time_remaining": selection["time_remaining"]
        }

    def _place_floating_tasks(self, floating_tasks: list[Task], occupied_times: list[tuple]) -> list[dict]:
        """Place floating tasks into available time slots.

        Phase 2 of scheduling: after fixed-time tasks are placed, greedily fit
        floating tasks into the remaining available slots using the owner's
        sort preference.

        Args:
            floating_tasks: List of tasks with no fixed scheduled time.
            occupied_times: List of (start_minute, end_minute) tuples already occupied.

        Returns:
            List of scheduled task dictionaries with 'task', 'start_time', 'end_time', 'type'.
        """
        timed_tasks = []
        available_slots = self.find_available_slots(occupied_times)

        if not available_slots:
            return timed_tasks

        all_floating = self.get_sorted_tasks(floating_tasks)
        slot_idx = 0

        for task in all_floating:
            task_minutes_needed = task.duration_minutes
            start_slot_idx = slot_idx

            # Check if we have enough consecutive slots for this task
            while task_minutes_needed > 0 and slot_idx < len(available_slots):
                task_minutes_needed -= 1
                slot_idx += 1

            # If task fits entirely, schedule it
            if task_minutes_needed <= 0:
                start_hour, start_minute = available_slots[start_slot_idx]
                end_minutes = self._time_to_minutes(f"{start_hour:02d}:{start_minute:02d}") + task.duration_minutes
                end_hour = end_minutes // 60
                end_minute = end_minutes % 60

                timed_tasks.append({
                    "task": task,
                    "start_time": f"{start_hour:02d}:{start_minute:02d}",
                    "end_time": f"{end_hour:02d}:{end_minute:02d}",
                    "type": "floating"
                })

        return timed_tasks

    def schedule_with_times(self, available_minutes: int) -> dict:
        """Fit tasks into time slots, honoring fixed-time constraints and availability windows.

        Two-phase scheduling:
        Phase 1: Place fixed-time tasks (user-pinned) in priority order.
        Phase 2: Fit floating tasks into remaining available slots.

        Args:
            available_minutes: Total minutes available for the day.

        Returns:
            Dictionary with 'timed_tasks', 'scheduled_tasks', 'skipped_tasks', 'time_remaining', and 'warnings'.
        """
        schedule_dict = self.build_schedule(available_minutes)
        scheduled_tasks = schedule_dict["scheduled_tasks"]

        partitioned = self.partition_tasks(scheduled_tasks)
        fixed_tasks = partitioned["fixed"]
        floating_tasks = partitioned["floating"]

        timed_tasks = []
        occupied_times = []
        fixed_time_warnings = []
        rejected_fixed_tasks = []

        # Phase 1: Place fixed-time tasks in priority order (highest priority first)
        sorted_fixed = self.get_sorted_tasks(fixed_tasks)

        for task in sorted_fixed:
            task_start = self._time_to_minutes(task.scheduled_time)
            task_end = task_start + task.duration_minutes
            hour, minute = map(int, task.scheduled_time.split(":"))

            if not self._time_in_window(hour, minute):
                fixed_time_warnings.append(
                    f"Warning: '{task.description}' scheduled for {task.scheduled_time} is outside availability windows. Skipping."
                )
                rejected_fixed_tasks.append(task)
                continue

            if not self._can_fit_in_window(hour, minute, task.duration_minutes):
                fixed_time_warnings.append(
                    f"Warning: '{task.description}' scheduled for {task.scheduled_time} doesn't fit in available windows. Skipping."
                )
                rejected_fixed_tasks.append(task)
                continue

            # Check for collision with already-placed fixed tasks
            collision = any(
                not (task_end <= start or task_start >= end)
                for start, end in occupied_times
            )

            if collision:
                fixed_time_warnings.append(
                    f"Warning: '{task.description}' scheduled for {task.scheduled_time} conflicts with another fixed task. Skipping."
                )
                rejected_fixed_tasks.append(task)
                continue

            end_time = self._minutes_to_time(task_end)

            timed_tasks.append({
                "task": task,
                "start_time": task.scheduled_time,
                "end_time": end_time,
                "type": "fixed"
            })

            occupied_times.append((task_start, task_end))

        # Phase 2: Place floating tasks into remaining available slots
        all_floating = floating_tasks + rejected_fixed_tasks
        floating_timed = self._place_floating_tasks(all_floating, occupied_times)
        timed_tasks.extend(floating_timed)

        # Detect conflicts in final schedule
        conflict_warnings = self.detect_conflicts(timed_tasks)
        all_warnings = fixed_time_warnings + conflict_warnings

        return {
            "timed_tasks": timed_tasks,
            "scheduled_tasks": scheduled_tasks,
            "skipped_tasks": schedule_dict["skipped_tasks"],
            "time_remaining": schedule_dict["time_remaining"],
            "warnings": all_warnings
        }

    def explain_schedule(self, schedule: dict) -> str:
        """Generate a human-readable explanation of the daily schedule with reasoning.

        Formats a schedule dictionary into a human-readable plan with:
        - Task list organized by format (timed, by pet, or by completion status)
        - Reasoning section explaining the sorting/selection strategy
        - Warnings about conflicts or skipped tasks
        - Time remaining and summary

        Args:
            schedule: Dictionary returned by build_schedule() or schedule_with_times().

        Returns:
            Formatted string ready for display or printing.
        """
        if not schedule.get("scheduled_tasks"):
            return "No tasks scheduled for today."

        explanation = f"Daily plan for {self.owner.name}:\n"

        # Handle different output formats
        if "timed_tasks" in schedule:
            # Time-slot format
            fixed_tasks = []
            floating_tasks = []
            for timed_task in schedule["timed_tasks"]:
                task = timed_task["task"]
                start = timed_task["start_time"]
                end = timed_task["end_time"]
                task_type = timed_task.get("type", "floating")

                line = f"\n  {start} - {end}: {task.description} ({task.duration_minutes} min) [priority: {task.priority}]"
                if task_type == "fixed":
                    fixed_tasks.append(line)
                else:
                    floating_tasks.append(line)

            if fixed_tasks:
                explanation += "\n(Fixed-time tasks):"
                explanation += "".join(fixed_tasks)
            if floating_tasks:
                explanation += "\n\n(Floating tasks):"
                explanation += "".join(floating_tasks)

            # Separate conflict warnings from other warnings
            if schedule.get("warnings"):
                conflict_warnings = [w for w in schedule["warnings"] if w.startswith("Conflict:")]
                other_warnings = [w for w in schedule["warnings"] if not w.startswith("Conflict:")]

                if conflict_warnings:
                    explanation += "\n\n⚠️  SCHEDULING CONFLICTS DETECTED:"
                    for warning in conflict_warnings:
                        explanation += f"\n  {warning}"

                if other_warnings:
                    explanation += "\n\n(Other warnings):"
                    for warning in other_warnings:
                        explanation += f"\n  {warning}"
        elif isinstance(schedule["schedule"], dict):
            # Check if it's filtered by completion or by pet
            if "completed" in schedule["schedule"] or "pending" in schedule["schedule"]:
                # Completion filter format
                if schedule["schedule"].get("completed"):
                    explanation += "\n\nCompleted:"
                    for task in schedule["schedule"]["completed"]:
                        explanation += f"\n  - {task.description} ({task.duration_minutes} min) [priority: {task.priority}]"
                if schedule["schedule"].get("pending"):
                    explanation += "\n\nPending:"
                    for task in schedule["schedule"]["pending"]:
                        explanation += f"\n  - {task.description} ({task.duration_minutes} min) [priority: {task.priority}]"
            else:
                # Pet filter format (default)
                total_time = 0
                for pet_name, tasks in schedule["schedule"].items():
                    explanation += f"\n\n{pet_name}:"
                    for task in tasks:
                        explanation += f"\n  - {task.description} ({task.duration_minutes} min) [priority: {task.priority}]"
                        total_time += task.duration_minutes
                explanation += f"\n\nTotal time scheduled: {total_time} min / {self.owner.available_time} min available"

        # Add reasoning section based on sorting method
        explanation += "\n\n--- REASONING ---\n"
        explanation += self._explain_reasoning(schedule["scheduled_tasks"])

        # Explain skipped tasks
        if schedule.get("skipped_tasks"):
            explanation += f"\n\nSkipped ({len(schedule['skipped_tasks'])} tasks due to insufficient time): "
            skipped_by_priority = {}
            for task in schedule["skipped_tasks"]:
                if task.priority not in skipped_by_priority:
                    skipped_by_priority[task.priority] = []
                skipped_by_priority[task.priority].append(task.description)

            for priority in ["high", "medium", "low"]:
                if priority in skipped_by_priority:
                    explanation += f"\n  {priority.capitalize()}: {', '.join(skipped_by_priority[priority])}"

        explanation += f"\n\nTime remaining: {schedule['time_remaining']} min"

        return explanation

    def _explain_reasoning(self, scheduled_tasks: list[Task]) -> str:
        """Explain the reasoning behind the task ordering based on sort preference.

        Routes to the appropriate explanation method based on the owner's
        chosen sort preference (priority, duration, or pet).

        Args:
            scheduled_tasks: List of tasks that were scheduled for today.

        Returns:
            Human-readable explanation of the scheduling strategy.
        """
        if self.owner.sort_preference == "duration":
            return self._explain_duration_sort(scheduled_tasks)
        elif self.owner.sort_preference == "pet":
            return self._explain_pet_sort(scheduled_tasks)
        else:  # priority (default)
            return self._explain_priority_sort(scheduled_tasks)

    def _explain_priority_sort(self, scheduled_tasks: list[Task]) -> str:
        """Explain tasks ordered by priority.

        Generates a reasoning explanation for schedules where tasks were
        selected and ordered by priority (high → medium → low).

        Args:
            scheduled_tasks: List of tasks in the schedule.

        Returns:
            Formatted explanation of priority-based scheduling.
        """
        high = [t for t in scheduled_tasks if t.priority == "high"]
        medium = [t for t in scheduled_tasks if t.priority == "medium"]
        low = [t for t in scheduled_tasks if t.priority == "low"]

        explanation = ""
        if high:
            explanation += f"High priority ({len(high)} tasks): These were scheduled first as they are most important: "
            explanation += ", ".join([t.description for t in high]) + "\n"

        if medium:
            explanation += f"Medium priority ({len(medium)} tasks): Scheduled after high priority if time allowed: "
            explanation += ", ".join([t.description for t in medium]) + "\n"

        if low:
            explanation += f"Low priority ({len(low)} tasks): Scheduled if time remained: "
            explanation += ", ".join([t.description for t in low])

        return explanation.rstrip()

    def _explain_duration_sort(self, scheduled_tasks: list[Task]) -> str:
        """Explain tasks ordered by duration.

        Generates a reasoning explanation for schedules where tasks were
        selected and ordered by duration (shortest to longest).

        Args:
            scheduled_tasks: List of tasks in the schedule.

        Returns:
            Formatted explanation of duration-based scheduling.
        """
        sorted_by_duration = sorted(scheduled_tasks, key=lambda t: t.duration_minutes)
        explanation = "Tasks scheduled shortest-to-longest to fit more into the available time:\n"
        for task in sorted_by_duration:
            explanation += f"  - {task.description} ({task.duration_minutes} min)\n"
        return explanation.rstrip()

    def _explain_pet_sort(self, scheduled_tasks: list[Task]) -> str:
        """Explain tasks ordered by pet.

        Generates a reasoning explanation for schedules where tasks were
        grouped by pet, completing all tasks for one pet before moving to the next.

        Args:
            scheduled_tasks: List of tasks in the schedule.

        Returns:
            Formatted explanation of pet-based scheduling.
        """
        task_to_pet = {}
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                task_to_pet[task.id] = pet.name

        explanation = "Tasks grouped by pet to complete care for one pet before moving to the next:\n"
        current_pet = None
        pet_tasks = []
        for task in scheduled_tasks:
            pet_name = task_to_pet.get(task.id, "Unknown")
            if pet_name != current_pet:
                if pet_tasks:
                    explanation += ", ".join(pet_tasks) + "\n"
                explanation += f"  {pet_name}: "
                current_pet = pet_name
                pet_tasks = []
            pet_tasks.append(task.description)

        if pet_tasks:
            explanation += ", ".join(pet_tasks)

        return explanation

