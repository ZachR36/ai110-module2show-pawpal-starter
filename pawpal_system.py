from dataclasses import dataclass, field
from typing import list


@dataclass
class Task:
    id: int
    description: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_overdue(self, current_time) -> bool:
        pass


@dataclass
class Pet:
    id: int
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: int) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


class Owner:
    def __init__(self, name: str, available_time: int, preferences: dict = None):
        self.name = name
        self.available_time = available_time
        self.preferences = preferences if preferences else {}
        self.pets = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: int) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


# TODO: Decide whether to create a separate DailySchedule class or keep as dict/list
class Scheduler:
    def __init__(self, owner: Owner):
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def build_schedule(self, available_minutes: int) -> "DailySchedule":
        pass

    def explain_schedule(self, schedule: "DailySchedule") -> str:
        pass
