from dataclasses import dataclass, field
from datetime import datetime

# TODO: Add time-slot scheduling instead of just task lists
# Currently build_schedule returns tasks that fit in available_minutes, but doesn't assign specific times.
# The teacher's design expects output like "8:00am - Morning walk, 8:30am - Feeding, etc."
# This requires: (1) Owner input for available hours (start/end time), (2) assigning scheduled times to tasks, (3) updating explain_schedule to show times.

# TODO: Handle overdue tasks in prioritization
# Currently is_overdue() just checks the time, but overdue tasks should be boosted to the front of the schedule.
# This requires passing current_time through build_schedule and prioritize_tasks.

# TODO: Implement DailySchedule class
# Decide whether to create a separate DailySchedule class or keep schedule as a dict.
# Currently build_schedule returns a dict; a dedicated class would be cleaner.

# TODO: Incorporate owner preferences into scheduling
# Owner has a preferences dict, but it's not used in build_schedule or prioritize_tasks.
# We should use these preferences (e.g., "prefer morning walks") when ordering/timing tasks.


@dataclass
class Task:
    id: int
    description: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_overdue(self, current_time: datetime) -> bool:
        """Check if this task is overdue based on the current time."""
        if self.completed:
            return False
        return current_time.hour > 20


@dataclass
class Pet:
    id: int
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet's task list by ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks


class Owner:
    def __init__(self, name: str, available_time: int, preferences: dict = None):
        self.name = name
        self.available_time = available_time
        self.preferences = preferences if preferences else {}
        self.pets = []

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

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high → low) and duration."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (priority_order.get(t.priority, 3), t.duration_minutes))

    def build_schedule(self, available_minutes: int) -> dict:
        """Build a daily schedule fitting tasks into available time, grouped by pet."""
        tasks = self.get_tasks()
        prioritized = self.prioritize_tasks(tasks)

        schedule = {}
        time_remaining = available_minutes
        scheduled_tasks = []
        skipped_tasks = []

        for task in prioritized:
            if time_remaining >= task.duration_minutes:
                scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes
            else:
                skipped_tasks.append(task)

        for pet in self.owner.pets:
            pet_tasks = [t for t in scheduled_tasks if t in pet.get_tasks()]
            if pet_tasks:
                schedule[pet.name] = pet_tasks

        return {
            "schedule": schedule,
            "scheduled_tasks": scheduled_tasks,
            "skipped_tasks": skipped_tasks,
            "time_remaining": time_remaining
        }

    def explain_schedule(self, schedule: dict) -> str:
        """Generate a human-readable explanation of the daily schedule."""
        if not schedule.get("scheduled_tasks"):
            return "No tasks scheduled for today."

        explanation = f"Daily plan for {self.owner.name}:\n"
        total_time = 0

        for pet_name, tasks in schedule["schedule"].items():
            explanation += f"\n{pet_name}:\n"
            for task in tasks:
                explanation += f"  - {task.description} ({task.duration_minutes} min) [priority: {task.priority}]\n"
                total_time += task.duration_minutes

        explanation += f"\nTotal time scheduled: {total_time} min"

        if schedule.get("skipped_tasks"):
            explanation += f"\nSkipped ({len(schedule['skipped_tasks'])} tasks due to time constraints): "
            explanation += ", ".join([t.description for t in schedule["skipped_tasks"]])

        return explanation
